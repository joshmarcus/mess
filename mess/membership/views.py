from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext

from mess.membership.models import Member, Account
from mess.membership.forms import MemberForm

def member_list(request):
    page_name = 'Members'
    member_list = Member.objects.all()
    return render_to_response('membership/member_list.html', locals(),
                                context_instance=RequestContext(request))

def member(request, id_num):
    member = Member.objects.get(id=id_num)    
    page_name = member
    return render_to_response('membership/member.html', locals(),
                                context_instance=RequestContext(request))

def member_form(request, id=None):
    page_name = 'Member Form'
    if request.method == 'POST':
        if pk:
            member = Member.objects.get(id=id)
            form = MemberForm(request.POST, instance=member)
        else:
            form = MemberForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/member/list')
        else:
            pass
    else:
        if id:
            member = Member.objects.get(id=id)
            form = MemberForm(instance=member)
        else:
            form = MemberForm()
        return render_to_response('membership/member_form.html', locals(),
                                    context_instance=RequestContext(request))

def account_list(request):
    page_name = 'Accounts'
    account_list = Account.objects.all()
    return render_to_response('membership/account_list.html', locals(),
                                context_instance=RequestContext(request))

def account(request, id_num):
    name = Account.objects.get(id=id_num).name
    page_name = 'name'
    return render_to_response('membership/account.html', locals(),
                                context_instance=RequestContext(request))
