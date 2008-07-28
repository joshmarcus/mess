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
