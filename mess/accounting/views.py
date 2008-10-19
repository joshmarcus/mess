from datetime import date

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import get_template
from django.utils import simplejson

from mess.accounting import forms, models
from mess.accounting.forms import TransactionForm, CloseOutForm
from mess.accounting.models import Transaction, get_credit_choices, \
    get_debit_choices, get_todays_transactions, get_trans_total, Member, \
    Account
from mess.utils.search import search_for_string, account_members_dict

def thanks(request):
    page_name = 'Thank You'
    try:
        redirect = request.META.get('HTTP_REFERER')
    except:
        redirect = '/'
    return render_to_response('accounting/thanks.html', locals(),
                                context_instance=RequestContext(request))
    
def get_trans_of_type(type, d=date.today()):
    #d = date.today()
    return Transaction.objects.filter(date__year = d.year,
                                    date__month = d.month,
                                    date__day = d.day,
                                    debit_type = type,)

def save_credit_trans(request):
        d = TransactionForm(request.POST)
        if d.data['credit_type'] != 'N':
            data = {'account': d.data['account'], 'member': d.data['member'],
                'debit_type': 'N', 'debit': '0',
                'credit_type': d.data['credit_type'],
                'credit': d.data['credit'], 'note': d.data['note'],
                'ref': d.data['ref'], 'balance': '0'}
            f = TransactionForm(data)
            f.is_valid()
            f.save()

def save_debit_trans(request):
        d = TransactionForm(request.POST)
        if d.data['debit_type'] != 'N':
            data = {'account': d.data['account'], 'member': d.data['member'],
                'debit_type': d.data['debit_type'], 'debit': d.data['debit'],
                'credit_type': 'N', 'credit': '0', 'note': d.data['note'],
                'ref': d.data['ref'], 'balance': '0'}
            f = TransactionForm(data)
            f.is_valid()
            f.save()

def transaction_form(request):
    transactions = get_todays_transactions()
    page_name = 'Transactions'
    if request.method == 'POST':  
        save_credit_trans(request)        
        save_debit_trans(request)        
        return HttpResponseRedirect('thanks')
    form = TransactionForm()
    return render_to_response('accounting/transaction_form.html', locals(),
                                context_instance=RequestContext(request))


def cashier(request):
    context = RequestContext(request)
    if request.method == 'POST':
        save_credit_trans(request)
        save_debit_trans(request)
        return HttpResponseRedirect(reverse('accounting-thanks'))
    if 'search' in request.GET:
        search = request.GET['search']
        search_result = []
        if search == 'transactions':
            if 'account_id' in request.GET:
                account_id = request.GET.get('account_id')
                trans = Transaction.objects.filter(account=account_id)
                context['account_name'] = Account.objects.get(id=account_id).name
            else:
                d = date.today()
                trans = Transaction.objects.filter(date__year = d.year,
                                            date__month = d.month,
                                            date__day = d.day)
            context['transactions'] = trans
            return render_to_response('accounting/snippets/transactions.html', context)
        if 'account_id' in request.GET:
            account_id = request.GET.get('account_id')
            account_members = account_members_dict(account_id)
            for id, name in account_members.items():
                search_result.append({'id': id, 'name': name, 'account_member': True})
        if 'string' in request.GET:
            string = request.GET.get('string')
            if search == 'members':
                members = search_for_string('members', string)
                for id, name in members.items():
                    search_result.append({'id': id, 'name': name, 'account_member': False})
                result_set = {'results': search_result}
            elif search == 'accounts':
                result = []
                dict = search_for_string('accounts', string)
                for id, name in dict.items():
                    result.append({'id': id, 'name': name})
                result_set = {'results': result}
        if search == 'other_member':
            context['other_member_id'] =  request.GET.get('om_id')
            context['other_member_name'] = request.GET.get('om_name')
            context['account_name'] = request.GET.get('account_name')
            return render_to_response('accounting/snippets/confirm_other_member.html', context)
        return HttpResponse(simplejson.dumps(result_set), mimetype='application/javascript')
    context['page_name'] = 'Cashier'
    context['credit_choices'] = get_credit_choices('Staff', 'Cashier')
    context['debit_choices'] = get_debit_choices('Staff', 'Cashier')
    #form = TransactionForm()
    context['form'] = form
    context['transactions_today'] = get_todays_transactions()
    #return render_to_response('accounting/cashier.html', context,
    #                            context_instance=RequestContext(request))
    template = get_template('accounting/cashier.html')
    return HttpResponse(template.render(context))

def new_cashier(request):
    context = RequestContext(request)
    if request.method == 'POST':
        form = forms.CashierForm(request.POST)
    else:
        form = forms.CashierForm()
    context['form'] = form
    template = get_template('accounting/cashier.html')
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
        template = get_template('accounting/thanks.html')
        return HttpResponse(template.render(context))
    if not request.method == 'POST':
        if type == 'all':
            transactions = get_todays_transactions()
        else:
            transactions = get_trans_of_type(type)
        tran_list = {}
        user = request.user
        for t in transactions:
            if t.debit_type != 'N':
                tran_type = t.get_debit_type_display()
                amount = t.debit
            if t.credit_type != 'N':
                tran_type = t.get_credit_type_display()
                amount = t.credit
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

