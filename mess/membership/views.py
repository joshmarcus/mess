from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseRedirect
from django.template import RequestContext

from mess.membership.models import Member, Account
from mess.membership.forms import MemberForm

@permission_required('membership.can_view_list')
def member_list(request):
    page_name = 'Members'
    member_list = Member.objects.all()
    return render_to_response('membership/member_list.html', locals(),
                                context_instance=RequestContext(request))

@permission_required('membership.can_edit_own')
def member(request, id):
    member = get_object_or_404(Member, id=id)    
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
    return render_to_response('membership/member.html', locals(),
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
