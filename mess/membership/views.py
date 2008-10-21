from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core import paginator as p
from django.forms.models import modelformset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import get_template

#from mess.accounting import models as a_models
from mess.membership import forms, models
from mess.profiles import forms as profiles_forms
from mess.profiles import models as profiles_models

# number of members or accounts to show per page in respective lists
PER_PAGE = 20

@user_passes_test(lambda u: u.is_staff)
def member_list(request):
    context = RequestContext(request)
    member_objs = models.Member.objects.all()
    if 'sort_by' in request.GET:
        form = forms.MemberListFilterForm(request.GET)
        if form.is_valid():
            sort = form.cleaned_data['sort_by']
            if sort == 'alpha':
                member_objs.order_by('user__username')
            if sort == 'oldjoin':
                member_objs.order_by('date_joined')
            if sort == 'newjoin':
                member_objs.order_by('-date_joined')
    else:
        form = forms.MemberListFilterForm()
    context['form'] = form
    pager = p.Paginator(member_objs, PER_PAGE)
    context['pager'] = pager
    page_number = request.GET.get('p')
    context['page'] = get_current_page(pager, page_number)
    template = get_template('membership/member_list.html')
    return HttpResponse(template.render(context))

def member(request, username):
    user = get_object_or_404(User, username=username)
    if not request.user.is_staff and not (request.user.is_authenticated() 
            and request.user.id == user.id):
        return HttpResponseRedirect(reverse('login'))
    context = RequestContext(request)
    profile = user.get_profile()
    context['profile'] = profile
    member = get_object_or_404(models.Member, user=user)
    context['member'] = member
    # to get around silly {% url %} limits
    context['address_name'] = 'address'
    context['phone_name'] = 'phone'
    context['email_name'] = 'email'
    # this list should live somewhere else, but I don't know where:
    context['contact_media'] = ['address', 'phone', 'email']
    template = get_template('membership/member.html')
    return HttpResponse(template.render(context))

@user_passes_test(lambda u: u.is_staff)
def member_add(request):
    if not request.user.is_staff:
        return HttpResponseRedirect(reverse('login'))
    member = user = None
    # a fake profile (no profile should have an id of 0) will return
    # no addresses, phones, or emails
    profile = profiles_models.UserProfile(id=0)
    # TODO: need to grab user (and corresponding profile) from 
    # user_form on added member

@user_passes_test(lambda u: u.is_staff)
def member_edit(request, username):
    user = get_object_or_404(User, username=username)
    if not request.user.is_staff and not (request.user.is_authenticated() 
            and request.user.id == user.id):
        return HttpResponseRedirect(reverse('login'))
    profile = user.get_profile()
    member = get_object_or_404(models.Member, user=user)
    context = RequestContext(request)
    context['member'] = member
    is_errors = False
    if request.method == 'POST':
        user_form = forms.UserForm(request.POST, prefix='user', instance=user)
        member_form = forms.MemberForm(request.POST, prefix='member', 
                instance=member)
        related_accounts_form = forms.RelatedAccountsForm(member, request.POST,
                prefix='related')
        address_formset = profiles_forms.AddressFormSet(request.POST, 
                prefix='address',
                queryset=profile.addresses.all())
        phone_formset = profiles_forms.PhoneFormSet(request.POST,
                prefix='phone',
                queryset=profile.phones.all())
        email_formset = profiles_forms.EmailFormSet(request.POST,
                prefix='email',
                queryset=profile.emails.all())
        if (user_form.is_valid() and member_form.is_valid() and 
                related_accounts_form.is_valid() and address_formset.is_valid()
                and phone_formset.is_valid() and email_formset.is_valid()):
            user_form.save()
            member_form.save()
            related_accounts = related_accounts_form.cleaned_data['accounts']
            member.accounts = related_accounts
            member.save()
            # have to handle formset-saving manually because of m2m
            profile.addresses = fancy_save(address_formset)
            profile.phones = fancy_save(phone_formset)
            profile.emails = fancy_save(email_formset)
            profile.save()
            return HttpResponseRedirect(reverse('member', args=[username]))
        else:
            is_errors = True
    else:
        user_form = forms.UserForm(instance=user, prefix='user')
        member_form = forms.MemberForm(instance=member, prefix='member')
        related_accounts_form = forms.RelatedAccountsForm(member, 
                prefix='related')
        address_formset = profiles_forms.AddressFormSet(prefix='address',
                queryset=profile.addresses.all())
        phone_formset = profiles_forms.PhoneFormSet(prefix='phone',
                queryset=profile.phones.all())
        email_formset = profiles_forms.EmailFormSet(prefix='email',
                queryset=profile.emails.all())
    context['user_form'] = user_form
    context['member_form'] = member_form
    context['related_accounts_form'] = related_accounts_form
    context['formsets'] = [
        (address_formset, 'Addresses'), 
        (phone_formset, 'Phones'),
        (email_formset, 'Email Addresses'),
    ]
    context['is_errors'] = is_errors
    template = get_template('membership/member_form.html')
    return HttpResponse(template.render(context))

def fancy_save(formset):
    object_list = []
    for form in formset.forms:
        if form.cleaned_data.get('DELETE') or not form.cleaned_data:
            continue
        field_dict = {}
        for key in form.cleaned_data:
            if key not in ('DELETE', 'id'):
                field_dict[key] = form.cleaned_data[key]
        try:
            match = formset.model.objects.get(**field_dict)
        except formset.model.DoesNotExist:
            match = None
        if match:
            object_list.append(match)
        else:
            instance = formset.model()
            for key in form.cleaned_data:
                if key != 'id':
                    instance.__dict__[key] = form.cleaned_data[key]
            instance.save()
            object_list.append(instance)
    return object_list

#@user_passes_test(lambda u: u.is_staff)
def account_list(request):
    context = RequestContext(request)
    if request.user.is_staff:
        account_objs = models.Account.objects.all()
    elif request.user.is_authenticated():
        member = models.Member.objects.get(user=request.user)
        account_objs = member.accounts.all()
    else:
        return HttpResponseRedirect(reverse('login'))
    pager = p.Paginator(account_objs, PER_PAGE)
    context['pager'] = pager
    page_number = request.GET.get('p')
    context['page'] = get_current_page(pager, page_number)
    template = get_template('membership/account_list.html')
    return HttpResponse(template.render(context))

def account(request, id):
    account = get_object_or_404(models.Account, id=id)
    request_member = models.Member.objects.get(user=request.user)
    if not request.user.is_staff and not (request.user.is_authenticated() 
            and request_member in account.members.all()):
        return HttpResponseRedirect(reverse('login'))
    context = RequestContext(request)
    context['account'] = account
    transactions = account.transaction_set.all()
    context['transactions'] = transactions
    template = get_template('membership/account.html')
    return HttpResponse(template.render(context))

@user_passes_test(lambda u: u.is_staff)
def account_form(request, id):
    context = RequestContext(request)
    account = get_object_or_404(models.Account, id=id)
    # on POST, save data and return to account page
    if request.method == 'POST':
        form = forms.AccountForm(request.POST, instance=account)
        if form.is_valid():
            # PERMISSIONS # PERMISSIONS # PERMISSIONS #
            #   this should check permissions here    #  FIXME ???
            form.save()
            return HttpResponseRedirect('/membership/accounts/'+id)
    context['account'] = account
    form = forms.AccountForm(instance=account)
    context['form'] = form
    template = get_template('membership/account_form.html')
    return HttpResponse(template.render(context))

def get_current_page(pager, page_number):
    try:
        current_page = pager.page(page_number)
    except (p.PageNotAnInteger, TypeError):
        current_page = pager.page(1)
    return current_page


# This raw_list function outputs raw data for use by ajax and xmlhttprequest.
# Since the data is output raw, it doesn't use any template.
def raw_list(request):
	# try.  Catches non-integers, blank field, and missing field
	try: maxresults = int(request.GET.get('maxresults'))
	except: maxresults = 30

	# if we're listing accounts, list accounts matching pattern.
	# don't bother checking the location of *'s, assume account=*pattern*
	if request.GET.has_key('list') and request.GET.get('list') == 'accounts':
		account_list = models.Account.objects.all()
		if request.GET.has_key('account'):
			pattern = request.GET.get('account').replace('*','')
			account_list = account_list.filter(name__contains = pattern)
		account_names = account_list.values_list('name',flat=True)[:maxresults]
		return HttpResponse('\n'.join(account_names))

	# if we're listing members, list members matching account and/or pattern
	# note: This part may be SLOW due to [python-iteration] over all db entries
	if request.GET.has_key('list') and request.GET.get('list') == 'members':
		if request.GET.has_key('account'):
			acct = request.GET.get('account')
			member_list = models.Member.objects.filter(accounts__name = acct)
		else:
			member_list = models.Member.objects.all()
		mnames = [member.user.get_full_name() for member in member_list]

		# if we have a member pattern, filter it case-insensitively
# CAN'T SEEM TO DO A DATABASE FILTER ON member__user__get_full_name__contains
		if request.GET.has_key('member'):
			pattern = request.GET.get('member').replace('*','').lower()
			mnames = [m for m in mnames if m.lower().find(pattern) >= 0]

		mnames = mnames[:maxresults]
		return HttpResponse('\n'.join(mnames))		

	# if we're not sure what we're listing, fail
	return HttpResponse('error in request for raw list')
