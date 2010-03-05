from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.template.loader import get_template
from mess.telethon import forms
from mess.membership import models as m_models
from mess.accounting import models as a_models

def index(request):
    #if request.GET.get(''):
    form = forms.SearchForm(request.GET)
    if form.is_valid():
        if form.cleaned_data['member']:
            results = [form.cleaned_data['member']]
        else:
            results = m_models.Member.objects.all()
            if form.cleaned_data['criteria'] == 'pledges':
                results = results.filter(call__pledge_amount__isnull=False).order_by('accounts')
            elif form.cleaned_data['criteria'] == 'loans / donations':
                results = results.filter(call__loan__isnull=False).order_by('accounts')
            else:
                results = m_models.Member.objects.active().order_by('accounts')
    else:
        results = m_models.Member.objects.active().order_by('accounts')
        form = forms.SearchForm()
    return render_to_response('telethon/index.html', locals(),
            context_instance=RequestContext(request))

def member(request, username):
    user = get_object_or_404(User, username=username)
    member = user.get_profile()
    account = member.get_primary_account()
    if request.method == 'POST':
        form = forms.CallForm(request.POST)
        if form.is_valid():
            newcall = form.save(commit=False)
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
        form = forms.CallForm()
    context = RequestContext(request)
    context['member'] = member
    context['form'] = form
    context['account'] = account
    template = get_template('telethon/member.html')
    return HttpResponse(template.render(context))

