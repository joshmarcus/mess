from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import get_template

from mess.membership.forms import MemberForm
from mess.membership.models import Member, Account

@permission_required('membership.can_view_list')
def member_list(request):
    context = RequestContext(request)
    context['page_name'] = 'Members'
    context['member_list'] = Member.objects.all()
    template = get_template('membership/member_list.html')
    return HttpResponse(template.render(context))

@permission_required('membership.can_edit_own')
def member(request, username):
    context = RequestContext(request)
    user = get_object_or_404(User, username=username)
    profile = user.get_profile()
    context['profile'] = profile
    member = get_object_or_404(Member, user=user)
    context['member'] = member
    template = get_template('membership/member.html')
    return HttpResponse(template.render(context))

def member_form(request, id):
    context = RequestContext(request)
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

def account(request, id_num):
    name = Account.objects.get(id=id_num).name
    page_name = 'name'
    return render_to_response('membership/account.html', locals(),
                                context_instance=RequestContext(request))
