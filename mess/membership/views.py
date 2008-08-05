from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import get_template

from mess.membership.forms import MemberForm
from mess.membership.models import Member, Account

@user_passes_test(lambda u: u.is_staff)
def member_list(request):
    context = RequestContext(request)
    context['page_name'] = 'Members'
    context['member_list'] = Member.objects.all()
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
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/member/list')
    else:
        form = MemberForm(instance=member)
    context['form'] = form
    template = get_template('membership/member_form.html')
    return HttpResponse(template.render(context))

def account_list(request):
    context = RequestContext(request)
    account_list = Account.objects.all()
    context['account_list'] = account_list
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
    account_list = Account.objects.all()
    context['account_list'] = account_list
    template = get_template('membership/account_list.html')
    return HttpResponse(template.render(context))

# This raw_list function outputs raw data for use by ajax and xmlhttprequest.
# Since the data is output raw, it doesn't use any template.
def raw_list(request):
	# try.  Catches non-integers, blank field, and missing field
	try: maxresults = int(request.GET.get('maxresults'))
	except: maxresults = 20

	# if we're listing accounts, list accounts matching pattern.
	# don't bother checking the location of *'s, assume account=*pattern*
	if request.GET.has_key('list') and request.GET.get('list') == 'accounts':
		account_list = Account.objects.all()
		if request.GET.has_key('account'):
			pattern = request.GET.get('account').replace('*','')
			account_list = account_list.filter(name__contains = pattern)
		account_names = account_list.values_list('name',flat=True)[:maxresults]
		return HttpResponse('\n'.join(account_names))

	# if we're not sure what we're listing, fail
	return HttpResponse('error in request for raw list')
