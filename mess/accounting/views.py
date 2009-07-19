from datetime import date

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import get_template
from django.utils import simplejson

from mess.accounting import forms, models
from mess.accounting.forms import TransactionForm, CloseOutForm
from mess.membership import models as m_models

# cashier permission is the first if
@user_passes_test(lambda u: u.is_authenticated())
def transaction(request):
    if not m_models.cashier_permission(request):
        return HttpResponse('Sorry, you do not have cashier permission. %s' 
                             % request.META['REMOTE_ADDR'])

    context = RequestContext(request)
    if 'account' in request.GET:
        account_id = request.GET['account']
        account = m_models.Account.objects.get(id=account_id)
        context['account'] = account
        template = get_template('accounting/snippets/members.html')
        return HttpResponse(template.render(context))
    if request.method == 'POST':
        form = forms.TransactionForm(request.POST)
        if form.is_valid():
            form.save()
            form.instance.entered_by = request.user
            form.instance.save()
            return HttpResponseRedirect(reverse('transaction'))
    else:
        form = forms.TransactionForm()
    context['form'] = form
    today = date.today()
    transactions = models.Transaction.objects.filter(
            timestamp__day=today.day)
    context['transactions'] = transactions
    template = get_template('accounting/transaction.html')
    return HttpResponse(template.render(context))

def close_out(request, type='all'):
    """Page to reconcile the day's transactions."""
    context = RequestContext(request)
    context['global_nav'] = 'cashier'
    context['local_nav'] = 'close_out'
    if request.method == 'POST':
        post = request.POST
        context['p'] = post
        testing = {}
        for key, value in post.items():
            if key.split('_')[1] == 'reconcile':
                transaction = key.split('_')[0]                
                data = { 'transaction': transaction,
                        'reconciled_by': post.get('id_reconciled_by'),
                        'reconciled': True,
                        }
                #testing[transaction] = data
                f = CloseOutForm(data)
                f.is_valid()
                f.save()
        context['testing'] = testing
        return HttpResponseRedirect(reverse('close_out'))
    if not request.method == 'POST':
        if type == 'all':
            transactions = models.Transaction.objects.filter(
                    timestamp__day=date.today().day)
        else:
            transactions = get_trans_of_type(type)
        tran_list = {}
        user = request.user
        for t in transactions:
            if t.purchase_type:
                tran_type = t.get_purchase_type_display()
                amount = t.purchase_amount
            if t.payment_type:
                tran_type = t.get_payment_type_display()
                amount = t.payment_amount
            initial_data = {
                    'type': tran_type,
                    'amount': amount,
                    'transaction': t,
                    }
            tran_list[t.id] = initial_data
        context['tran_list'] = tran_list
        
    context['page_name'] = 'Close Out'
    d = date.today()
    context['date'] = d.strftime('%A, %B %d, %Y')    
    template = get_template('accounting/close_out.html')
    return HttpResponse(template.render(context))
