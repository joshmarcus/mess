from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core import paginator as p
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import get_template

from mess.membership import forms, models
from mess.profiles import forms as profile_forms

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

def member_form(request, username=None):
    if username:  # edit member
        user = get_object_or_404(User, username=username)
        if not request.user.is_staff and not (request.user.is_authenticated() 
                and request.user.id == user.id):
            return HttpResponseRedirect(reverse('login'))
        member = get_object_or_404(models.Member, user=user)
    else:  # add member
        if not request.user.is_staff:
            return HttpResponseRedirect(reverse('login'))
        member = None
    context = RequestContext(request)
    context['member'] = member
    if request.method == 'POST':
        user_form = forms.UserForm(request.POST, prefix='user', instance=user)
        member_form = forms.MemberForm(request.POST, prefix='member', 
            instance=member)
        if form[0].is_valid() and form[1].is_valid(): # and form[2].is_valid():
            # PERMISSIONS # PERMISSIONS # PERMISSIONS #
            #   this should check permissions here    #  FIXME ???
            for f in form: f.save()
            return HttpResponseRedirect('/membership/members/'+username)
    else:
        user_form = forms.UserForm(instance=user, prefix='user')
        member_form = forms.MemberForm(instance=member, prefix='member')
        address_formset = profile_forms.AddressFormSet(
                queryset=user.get_profile().addresses.all())
        phone_formset = profile_forms.PhoneFormSet(
                queryset=user.get_profile().phones.all())
        email_formset = profile_forms.EmailFormSet(
                queryset=user.get_profile().emails.all())
    context['user_form'] = user_form
    context['member_form'] = member_form
    context['formsets'] = [
        (address_formset, 'Addresses', 'address'), 
        (phone_formset, 'Phones', 'phone'),
        (email_formset, 'Email Addresses', 'email address'),
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
