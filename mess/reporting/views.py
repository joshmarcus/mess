from datetime import date, timedelta

from django.template import RequestContext
from django.shortcuts import render_to_response

from mess.accounting.models import Transaction
from mess.accounting.models import get_credit_choices, get_debit_choices
from mess.accounting.models import get_trans_total

def transaction_report(request, report='all'):
    """View to summerize transactions by type."""
    context = {}
    context['page_name'] = 'Transaction Summaries'
    if report == 'all':
        report_title = 'Summary of All Transactions'
        start_date = date(1900, 01, 01)        
        end_date = date.today() + timedelta(days=1) 
    elif report == 'today':
        start_date = date.today()
        end_date = start_date + timedelta(days=1)                
        formated_date = start_date.strftime('%A, %B %d, %Y')        
        report_title = 'Transactions Summary for Today, ' + formated_date
    elif report == 'yesterday':
        start_date = date.today() - timedelta(days=1)        
        end_date = date.today()
        formated_date = start_date.strftime('%A, %B %d, %Y')        
        report_title = 'Transactions Summary for Yesterday, ' + formated_date
    elif report == 'week':
        d = date.today()
        start_date = d - timedelta(days=d.weekday())        
        end_date = date.today()
        formated_date = start_date.strftime('%A, %B %d, %Y')        
        report_title = 'Transaction Summary for the Week Beginning ' + formated_date
    elif report == 'month':
        start_date = date(date.today().year, date.today().month , 01)        
        end_date = date.today()
        formated_date = start_date.strftime('%B, %Y')        
        report_title = 'Transactions Summary for the Month of ' + formated_date
    elif report == 'year':
        start_date =  date(date.today().year, 01, 01)
        end_date = date.today() + timedelta(days=1)
        formated_date = start_date.strftime('%Y')        
        report_title = 'Transaction Summary for Year of ' + formated_date
    elif report == 'custom':
        start_date = date.today() - timedelta(days=1)        
        end_date = date.today()
        formated_date = start_date.strftime('%A, %B %d, %Y')        
        report_title = 'Transaction Summary from ' + formated_date
        report_title += 'to ' + end_date.strftime('%A, %B %d, %Y')

    context['report_title'] = report_title
    context['total_credits'] = 0
    context['total_debits'] = 0
    #d = date.today()
    #context['date'] = d.strftime('%A, %B %d, %Y')
    for type, name in get_credit_choices('Staff'):
        if type != 'N':
            name = name.lower().replace(' ','_')
            total_name = 'total_' + name
            context[name] = Transaction.objects.filter(date__range =
                                                    (start_date, end_date),
                                                    credit_type = type,)
            context[total_name] = get_trans_total(context[name], 'credit')
            context['total_credits'] += context[total_name]
    for type, name in get_debit_choices('Staff'):
        if type != 'N':
            name = name.lower().replace(' ','_')
            total_name = 'total_' + name
            context[name] = Transaction.objects.filter(date__range =
                                                    (start_date, end_date),
                                                    debit_type = type,)
            context[total_name] = get_trans_total(context[name], 'debit')
            context['total_debits'] += context[total_name]

    return render_to_response('reporting/transactions_summary.html', context,
                                context_instance=RequestContext(request))


def transaction_list_report(request, report='all'):
    """View to list transactions."""
    context = {}
    context['page_name'] = 'Transactions'
    if report == 'all':
        report_title = 'All Transactions'
        start_date = date(1900, 01, 01)        
        end_date = date.today() + timedelta(days=1) 
    elif report == 'today':
        start_date = date.today()
        end_date = start_date + timedelta(days=1)                
        formated_date = start_date.strftime('%A, %B %d, %Y')        
        report_title = 'Transactions Summary for Today, ' + formated_date
    elif report == 'yesterday':
        start_date = date.today() - timedelta(days=1)        
        end_date = date.today()
        formated_date = start_date.strftime('%A, %B %d, %Y')        
        report_title = 'Transactions Summary for Yesterday, ' + formated_date
    elif report == 'week':
        d = date.today()
        start_date = d - timedelta(days=d.weekday())        
        end_date = date.today()
        formated_date = start_date.strftime('%A, %B %d, %Y')        
        report_title = 'Transaction Summary for the Week Beginning ' + formated_date
    elif report == 'month':
        start_date = date(date.today().year, date.today().month , 01)        
        end_date = date.today()
        formated_date = start_date.strftime('%B, %Y')        
        report_title = 'Transactions Summary for the Month of ' + formated_date
    elif report == 'year':
        start_date = date(date.today().year, 01, 01)  
        end_date = date.today() + timedelta(days=1)
        formated_date = start_date.strftime('%Y')        
        report_title = 'Transaction Summary for Year of ' + formated_date
    elif report == 'custom':
        start_date = date.today() - timedelta(days=1)        
        end_date = date.today()
        formated_date = start_date.strftime('%A, %B %d, %Y')        
        report_title = 'Transaction Summary from ' + formated_date
        report_title += 'to ' + end_date.strftime('%A, %B %d, %Y')

    context['report_title'] = report_title
    context['transactions'] = Transaction.objects.filter(date__range =
                                                    (start_date, end_date),)
    
    return render_to_response('reporting/transactions_list.html', context,
                                context_instance=RequestContext(request))



