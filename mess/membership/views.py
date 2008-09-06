from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core import paginator as p
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import get_template

from mess.membership.forms import AccountForm
from mess.membership.forms import MemberForm, UserForm, UserProfileForm
from mess.membership.models import Member, Account

# number of members or accounts to show per page in respective lists
PER_PAGE = 20

@user_passes_test(lambda u: u.is_staff)
def member_list(request):
    context = RequestContext(request)
    member_objs = Member.objects.all()
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
    member = get_object_or_404(Member, user=user)
    context['member'] = member
    template = get_template('membership/member.html')
    context['caneditprofile'] = True
    # this list should live somewhere else, but I don't know where:
    context['contactmedia'] = ['address', 'phone', 'email']
    return HttpResponse(template.render(context))

def member_form(request, username=None):
    if username:
        user = get_object_or_404(User, username=username)
        if not request.user.is_staff and not (request.user.is_authenticated() 
                and request.user.id == user.id):
            return HttpResponseRedirect(reverse('login'))
        member = get_object_or_404(Member, user=user)
    else:
        if not request.user.is_staff:
            return HttpResponseRedirect(reverse('login'))
        member = None
    context = RequestContext(request)
    context['member'] = member
    if request.method == 'POST':
        form = [ MemberForm(request.POST, prefix="member", instance=member),
			UserForm(request.POST, prefix="user", instance=user) ]
#			UserProfileForm(request.POST, prefix="userprofile", instance=user.get_profile()) ]
        if form[0].is_valid() and form[1].is_valid(): # and form[2].is_valid():
            # PERMISSIONS # PERMISSIONS # PERMISSIONS #
            #   this should check permissions here    #  FIXME ???
            for f in form: f.save()
            return HttpResponseRedirect('/membership/members/'+username)
    else:
        form = [ MemberForm(instance=member, prefix="member"),
            UserForm(instance=user, prefix="user") ]
#           UserProfileForm(instance=user.get_profile(), prefix="userprofile") ]
    context['form'] = form
    template = get_template('membership/member_form.html')
    return HttpResponse(template.render(context))

def account_list(request):
    context = RequestContext(request)
    account_objs = Account.objects.all()
    pager = p.Paginator(account_objs, PER_PAGE)
    context['pager'] = pager
    page_number = request.GET.get('p')
    context['page'] = get_current_page(pager, page_number)
    template = get_template('membership/account_list.html')
    return HttpResponse(template.render(context))

def account(request, id):
    context = RequestContext(request)
    account = get_object_or_404(Account, id=id)
    context['account'] = account
    template = get_template('membership/account.html')
    return HttpResponse(template.render(context))

def account_form(request, id):
    context = RequestContext(request)
    account = get_object_or_404(Account, id=id)
    # on POST, save data and return to account page
    if request.method == 'POST':
        form = AccountForm(request.POST, instance=account)
        if form.is_valid():
            # PERMISSIONS # PERMISSIONS # PERMISSIONS #
            #   this should check permissions here    #  FIXME ???
            form.save()
            return HttpResponseRedirect('/membership/accounts/'+id)
    context['account'] = account
    form = AccountForm(instance=account)
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
		account_list = Account.objects.all()
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
			member_list = Member.objects.filter(accounts__name = acct)
		else:
			member_list = Member.objects.all()
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
