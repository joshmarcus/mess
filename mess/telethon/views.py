from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.template.loader import get_template
from mess.telethon import forms
from mess.membership import models as m_models
from mess.accounting import models as a_models

def index(request):
    # jump to member
    if request.GET.get('member'):
        try:
            member = m_models.Member.objects.get(id=request.GET['member'])
        except (ValueError, m_models.Member.DoesNotExist):
            pass
        else:
            return HttpResponseRedirect(reverse('telethon-member', 
                args=[member.user.username]))
    # or search
    form = forms.JumpToMemberForm()
    if request.GET.get('search'):
        searchform = forms.SearchForm(request.GET)
        if searchform.is_valid():
            results = m_models.Member.objects.active()
            if searchform.cleaned_data['search'] != '':
                q = searchform.cleaned_data['search']
                results = results.filter(Q(user__first_name__icontains=q)
                                       | Q(user__last_name__icontains=q)
                                       | Q(accounts__name__icontains=q)
                                       | Q(call__note__icontains=q)
                                       | Q(call__caller__username=q))
            if searchform.cleaned_data['criteria'] == 'pledges':
                results = results.filter(call__pledge_amount__isnull=False)
            elif searchform.cleaned_data['criteria'] == 'loans / donations':
                results = results.filter(call__loan__isnull=False)
    else:
        results = m_models.Member.objects.active()
        searchform = forms.SearchForm()
    results = [x for x in results.order_by('accounts').distinct()]
    for result in results:
        result.do_not_call = False
        for call in result.call_set.all():
            if call.do_not_call:
                result.do_not_call = True
    return render_to_response('telethon/index.html', locals(),
            context_instance=RequestContext(request))

def member(request, username):
    user = get_object_or_404(User, username=username)
    member = user.get_profile()
    account = member.get_primary_account()
    if request.method == 'POST':
        callform = forms.CallForm(request.POST)
        if callform.is_valid():
            newcall = callform.save(commit=False)
            newcall.callee = member
            newcall.caller = request.user
            if newcall.loan_term:
                gift = a_models.Transaction(account=account, member=member,
                    purchase_type='G', purchase_amount=newcall.pledge_amount,
                    entered_by=request.user)
                gift.save()
                newcall.loan = gift
            newcall.save()
            return HttpResponseRedirect(reverse('telethon-member',args=[username]))
    else:
        callform = forms.CallForm()
    do_not_call = False
    for call in member.call_set.all():
        if call.do_not_call:
            do_not_call = True
    context = RequestContext(request)
    # sorry, this has to be called form for the autocomplete js to be included
    context['form'] = forms.JumpToMemberForm()  
    context['searchform'] = forms.SearchForm()
    context['member'] = member
    context['callform'] = callform
    context['account'] = account
    context['do_not_call'] = do_not_call
    template = get_template('telethon/member.html')
    return HttpResponse(template.render(context))

