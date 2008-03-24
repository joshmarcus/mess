from datetime import date

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.utils import simplejson
from django.template import RequestContext

from mess.accounting.models import Transaction
from mess.accounting.models import get_credit_choices, get_debit_choices
from mess.membership.models import Member, Account
from mess.accounting.forms import TransactionForm

def thanks(request):
    page_name = 'Thank You'
    try:
        redirect = request.META.get('HTTP_REFERER')
    except:
        redirect = '/'
    return render_to_response('accounting/thanks.html', locals(),
                                context_instance=RequestContext(request))

def live_search(request):
    """ If GET has a 'search' key it returns primary keys and names
    based on the type of 'search' requested.

    Search Values:
        accountMembers: Returns members belonging to an account.
            account_members: {'id', 'name'}
        allMembers: Returns all members.
            account_members: {'id', 'name'}
        allAccounts: Returns all accounts.
            account_members: {'id', 'name'}
        getMembers: Returns members with names matcing a string.
            account_members: {'id', 'name'}
        getAccounts: Returns accounts with names matching a string.
            account_members: {'id', 'name'}
                
    search_dict = {'account_members': {},
                    'all_members': {}, 'all_accounts': {},
                    'get_members': {}, 'get_accounts': {},
                }
        
    """
    if request.GET.has_key('search'):
        search = request.GET.get('search')
        search_dict = {'account_members': {},
                    'all_members': {}, 'all_accounts': {},
                    'get_members': {}, 'get_accounts': {},
                    }
        if search == 'accountMembers' and request.GET.has_key('accountID'):
            # Get the members that belong to an account.
            list = Account.objects.get(id=request.GET.get('accountID'))
            for i in list.members.all():
                search_dict['account_members'][i.id] = i.person.name
        if search == 'allAccounts':
            # Get all accounts.
            list = Account.objects.all()
            for i in list:
                search_dict['all_accounts'][i.id] = i.name
        if search == 'allMembers':
            # Get all members.
            list = Member.objects.all()
            for i in list:
                search_dict['all_members'][i.id] = i.person.name
        if request.GET.has_key('string'):
            if request.GET.get('string'):
                string = request.GET.get('string')
                if search == 'getAccounts':
                    # Search for account names matching a string.
                    list = Account.objects.filter(name__icontains=string)
                    for i in list:
                        search_dict['get_accounts'][i.id] = i.name
                if search == 'getMembers':
                    # Search for member names matching a string.
                    list = Member.objects.filter(person__name__icontains=string)
                    for i in list:
                        search_dict['get_members'][i.id] = i.person.name
                    if request.GET.has_key('accountID'):
                        accounts = Account.objects.get(id=request.GET.get('accountID'))
                        for i in accounts.members.all():
                            search_dict['account_members'][i.id] = i.person.name
    return search_dict


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
    """accounting view for the transaction form."""
    
    page_name = 'Cashier'
    if not request.method == 'POST' and not request.GET.has_key('search'):
        credit_choices = get_credit_choices('Cashier', 'Cashier')
        debit_choices = get_debit_choices('Cashier', 'Cashier')
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
