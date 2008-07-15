from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import get_template

from mess.membership.forms import MemberForm
from mess.membership.models import Member, Account
from mess.people.models import Person

@permission_required('membership.can_view_list')
def member_list(request):
    context = RequestContext(request)
    context['page_name'] = 'Members'
    context['member_list'] = Member.objects.all()
    template = get_template('membership/member_list.html')
    return HttpResponse(template.render(context))

@permission_required('membership.can_edit_own')
def member(request, id):
    context = RequestContext(request)
    user = get_object_or_404(User, id=id)
    person = get_object_or_404(Person, user=user)
    member = get_object_or_404(Member, person=person)    
    context['member'] = member
    if request.method == 'POST':
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/member/list')
    else:
        form = MemberForm(instance=member)
    context['form'] = form
    template = get_template('membership/member.html')
    return HttpResponse(template.render(context))

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
