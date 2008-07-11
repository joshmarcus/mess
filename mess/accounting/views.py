from datetime import date

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.utils import simplejson
from django.template import RequestContext
from django.template.loader import render_to_string

from mess.accounting.models import Transaction
from mess.accounting.models import get_credit_choices, get_debit_choices
from mess.membership.models import Member, Account
from mess.accounting.forms import TransactionForm
from mess.utils.search import search_for_string, account_members_dict

def thanks(request):
    page_name = 'Thank You'
    try:
        redirect = request.META.get('HTTP_REFERER')
    except:
        redirect = '/'
    return render_to_response('accounting/thanks.html', locals(),
                                context_instance=RequestContext(request))

def get_todays_transactions():
    d = date.today()
    return Transaction.objects.filter(date__year = d.year,
                                        date__month = d.month,
                                        date__day = d.day)
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
    if not request.method == 'POST':  
        form = TransactionForm()
    else:
        save_credit_trans(request)        
        save_debit_trans(request)        
        return HttpResponseRedirect('thanks')
    return render_to_response('accounting/transaction_form.html', locals(),
                                context_instance=RequestContext(request))

def cashier(request):
    context = {}
    if request.method == 'POST':
        save_credit_trans(request)
        save_debit_trans(request)
        return HttpResponseRedirect('thanks')
    elif 'search' in request.GET:
        search = request.GET.get('search')
        if search == 'transactions':
            if 'account_id' in request.GET:
                account_id = request.GET.get('account_id')
                trans = Transaction.objects.filter(account = account_id)
                context['account_name'] = Account.objects.get(id = account_id).name
            else:
                d = date.today()
                trans = Transaction.objects.filter(date__year = d.year,
                                            date__month = d.month,
                                            date__day = d.day)
            context['transactions'] = trans
            return render_to_response('xhr/transactions.html', context)
        if 'account_id' in request.GET:
            account_id = request.GET.get('account_id')
            account_members = account_members_dict(account_id)
            context['account_members'] = account_members
        if 'string' in request.GET:
            string = request.GET.get('string')
            if search == 'members':
                context['members'] = search_for_string('members', string)
            elif search == 'accounts':
                context['accounts'] = search_for_string('accounts', string)
        if search == 'other_member':
            context['other_member_id'] =  request.GET.get('om_id')
            context['other_member_name'] = request.GET.get('om_name')
            context['account_name'] = request.GET.get('account_name')
            return render_to_response('xhr/confirm_other_member.html', context)
        return render_to_response('xhr/list.html', context)
    else:
        context['page_name'] = 'Cashier'
        context['credit_choices'] = get_credit_choices('Cashier', 'Cashier')
        context['debit_choices'] = get_debit_choices('Cashier', 'Cashier')
        form = TransactionForm()
        context['transactions_today'] = get_todays_transactions()
        return render_to_response('accounting/cashier.html', context,
                                    context_instance=RequestContext(request))

def close_out(request):
    """Page to reconcile the day's transactions."""
    context = {}
    return render_to_response('accounting/close_out.html', context,
                                context_instance=RequestContext(request))

def member_transaction(request):
    """accounting view for the transaction form."""
    role = 'Member'
    page_name = 'Member Trans'
    if not request.method == 'POST' and not request.GET.has_key('search'):
        credit_choices = get_credit_choices(role)
        debit_choices = get_debit_choices(role)
        form = TransactionForm()
        transactions = get_todays_transactions()
        transaction_title = 'Today\'s Transactions'
        return render_to_response('accounting/cashier.html', locals(),
                                    context_instance=RequestContext(request))
    elif request.GET.has_key('search'):
        search_dict = live_search(request)
        return HttpResponse(simplejson.dumps(search_dict),
                            mimetype='application/javascript')
    else:
        save_credit_trans(request)        
        save_debit_trans(request)        
        return HttpResponseRedirect('thanks')
 
    return render_to_response('accounting/cashier.html', locals(),
                                context_instance=RequestContext(request))

def staff_transaction(request):
    """accounting view for the transaction form."""
    role = 'Staff'
    page_name = 'Staff Trans'
    if not request.method == 'POST' and not request.GET.has_key('search'):
        credit_choices = get_credit_choices(role)
        debit_choices = get_debit_choices(role)
        form = TransactionForm()
        transactions = get_todays_transactions()
        transaction_title = 'Today\'s Transactions'
        return render_to_response('accounting/cashier.html', locals(),
                                    context_instance=RequestContext(request))
    elif request.GET.has_key('search'):
        search_dict = live_search(request)
        return HttpResponse(simplejson.dumps(search_dict),
                            mimetype='application/javascript')
    else:
        save_credit_trans(request)        
        save_debit_trans(request)        
        return HttpResponseRedirect('thanks')
 
    return render_to_response('accounting/cashier.html', locals(),
                                context_instance=RequestContext(request))
