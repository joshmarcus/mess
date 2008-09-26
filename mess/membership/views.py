from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core import paginator as p
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import get_template

from mess.membership import forms, models
from mess.profiles import forms as profiles_forms
from mess.profiles import models as profiles_models

# number of members or accounts to show per page in respective lists
PER_PAGE = 20

@user_passes_test(lambda u: u.is_staff)
def member_list(request):
    context = RequestContext(request)
    member_objs = models.Member.objects.all()
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
    template = get_template('membership/member.html')
    context['caneditprofile'] = True
    # this list should live somewhere else, but I don't know where:
    context['contactmedia'] = ['address', 'phone', 'email']
    return HttpResponse(template.render(context))

def member_add(request):
    if not request.user.is_staff:
        return HttpResponseRedirect(reverse('login'))
    member = user = None
    # a fake profile (no profile should have an id of 0) will return
    # no addresses, phones, or emails
    profile = profiles_models.UserProfile(id=0)
    # TODO: need to grab user (and corresponding profile) from 
    # user_form on added member

def member_edit(request, username):
    user = get_object_or_404(User, username=username)
    if not request.user.is_staff and not (request.user.is_authenticated() 
            and request.user.id == user.id):
        return HttpResponseRedirect(reverse('login'))
    profile = user.get_profile()
    member = get_object_or_404(models.Member, user=user)
    context = RequestContext(request)
    context['member'] = member
    if request.method == 'POST':
        user_form = forms.UserForm(request.POST, prefix='user', instance=user)
        member_form = forms.MemberForm(request.POST, prefix='member', 
            instance=member)
        address_formset = profiles_forms.AddressFormSet(request.POST, 
                prefix='addresses',
                queryset=profile.addresses.all())
        phone_formset = profiles_forms.PhoneFormSet(request.POST,
                prefix='phones',
                queryset=profile.phones.all())
        email_formset = profiles_forms.EmailFormSet(request.POST,
                prefix='emails',
                queryset=profile.emails.all())
        if (user_form.is_valid() and member_form.is_valid() and 
                address_formset.is_valid() and phone_formset.is_valid() and
                email_formset.is_valid()):
            user_form.save()
            member_form.save()
            address_instances = address_formset.save(commit=False)
            for address in address_instances:
                matches = profiles_models.Address.objects.filter(
                    type=address.type,
                    address1=address.address1,
                    address2=address.address2,
                )
                if matches:
                    first_match = matches[0]
                    profile.addresses.add(first_match)
                else:
                    address.save()
                    profile.addresses.add(address)
            phone_instances = phone_formset.save(commit=False)
            for phone in phone_instances:
                matches = profiles_models.Phone.objects.filter(
                    type=phone.type,
                    number=phone.number,
                    ext=phone.ext,
                )
                if matches:
                    first_match = matches[0]
                    profile.phones.add(first_match)
                else:
                    phone.save()
                    profile.phones.add(phone)
            email_instances = email_formset.save(commit=False)
            for email in email_instances:
                matches = profiles_models.Email.objects.filter(
                    type=email.type,
                    email=email.email,
                )
                if matches:
                    first_match = matches[0]
                    profile.emails.add(first_match)
                else:
                    email.save()
                    profile.emails.add(email)
            return HttpResponseRedirect(reverse('member', args=[username]))
    else:
        user_form = forms.UserForm(instance=user, prefix='user')
        member_form = forms.MemberForm(instance=member, prefix='member')
        address_formset = profiles_forms.AddressFormSet(prefix='addresses',
                queryset=profile.addresses.all())
        phone_formset = profiles_forms.PhoneFormSet(prefix='phones',
                queryset=profile.phones.all())
        email_formset = profiles_forms.EmailFormSet(prefix='emails',
                queryset=profile.emails.all())
    context['user_form'] = user_form
    context['member_form'] = member_form
    context['formsets'] = [
        (address_formset, 'Addresses', 'address'), 
        (phone_formset, 'Phones', 'phone'),
        (email_formset, 'Email Addresses', 'email'),
    ]
    template = get_template('membership/member_form.html')
    return HttpResponse(template.render(context))

def account_list(request):
    context = RequestContext(request)
    account_objs = models.Account.objects.all()
    pager = p.Paginator(account_objs, PER_PAGE)
    context['pager'] = pager
    page_number = request.GET.get('p')
    context['page'] = get_current_page(pager, page_number)
    template = get_template('membership/account_list.html')
    return HttpResponse(template.render(context))

def account(request, id):
    context = RequestContext(request)
    account = get_object_or_404(models.Account, id=id)
    context['account'] = account
    template = get_template('membership/account.html')
    return HttpResponse(template.render(context))

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
