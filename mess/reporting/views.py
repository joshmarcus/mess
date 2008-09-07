from datetime import date, timedelta
import time

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse

from mess.accounting.models import Transaction
from mess.accounting.models import get_credit_choices, get_debit_choices
from mess.accounting.models import get_trans_total

from mess.utils.search import list_usernames_from_fullname

def transaction_list_report(request):
    # c is the context to be passed to the template
    c = RequestContext(request)
    c['page_name'] = 'Transaction List'
    c['report_title'] = 'List of Transactions Matching Filter'

    # start with all transactions
    trans = Transaction.objects

    # if account or member specified, filter that
    if request.GET.has_key('account'): 
        c['account']=request.GET.get('account')
        if c['account'] != "":
            trans = trans.filter(account__name = c['account'])
    if request.GET.has_key('member'):
        c['member'] = request.GET.get('member')
        if c['member'] != "":
            c['usernames'] = list_usernames_from_fullname(c['member'])
            trans = trans.filter(member__user__username__in = c['usernames'])

    # Filter date range -- default to 1900-today.
    # If query date is invalid, error is ugly.  But that shouldn't happen.
    # strptime is hard to use, so here I do yyyy-mm-dd2date as slices.
    # End would be midnight before, but we want midnight after, so timedelta.
    if request.GET.has_key('start'):
        ymd = request.GET.get('start')
        c['start'] = date(int(ymd[:4]),int(ymd[5:7]),int(ymd[8:]))
    else: c['start'] = date(1900,1,1)
    if request.GET.has_key('end'): 
        ymd = request.GET.get('end')
        c['end'] = date(int(ymd[:4]),int(ymd[5:7]),int(ymd[8:]))
    else: c['end'] = date.today()
    if c['end'] < c['start']: (c['start'],c['end']) = (c['end'],c['start'])
    trans = trans.filter(date__range=(c['start'], c['end']+timedelta(days=1)))

    c['transactions'] = trans
    return render_to_response('reporting/transactions_list.html', c)


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
        formatted_date = start_date.strftime('%A, %B %d, %Y')        
        report_title = 'Transactions Summary for Today, %s' % formatted_date
    elif report == 'yesterday':
        start_date = date.today() - timedelta(days=1)        
        end_date = date.today()
        formatted_date = start_date.strftime('%A, %B %d, %Y')        
        report_title = 'Transactions Summary for Yesterday, ' + formatted_date
    elif report == 'week':
        d = date.today()
        start_date = d - timedelta(days=d.weekday())        
        end_date = date.today() + timedelta(days=1)
        formatted_date = start_date.strftime('%A, %B %d, %Y')        
        report_title = 'Transaction Summary for the Week Beginning ' + formatted_date
    elif report == 'month':
        start_date = date(date.today().year, date.today().month , 01)        
        end_date = date.today() + timedelta(days=1)
        formatted_date = start_date.strftime('%B, %Y')        
        report_title = 'Transactions Summary for the Month of ' + formatted_date
    elif report == 'year':
        start_date =  date(date.today().year, 01, 01)
        end_date = date.today() + timedelta(days=1)
        formatted_date = start_date.strftime('%Y')        
        report_title = 'Transaction Summary for Year of ' + formatted_date
    elif report == 'custom':
        start_date = date.today() - timedelta(days=1)        
        end_date = date.today()
        formatted_date = start_date.strftime('%A, %B %d, %Y')        
        report_title = 'Transaction Summary from ' + formatted_date
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

    #def transaction_list_report(request, report='all'):
#    """View to list transactions."""
#    context = {}
#    context['page_name'] = 'Transactions'
#    if report == 'all':
#        report_title = 'All Transactions'
#        start_date = date(1900, 01, 01)        
#        end_date = date.today() + timedelta(days=1) 
#    elif report == 'today':
#        start_date = date.today()
#        end_date = start_date + timedelta(days=1)                
#        formatted_date = start_date.strftime('%A, %B %d, %Y')        
#        report_title = 'Transactions Summary for Today, ' + formatted_date
#    elif report == 'yesterday':
#        start_date = date.today() - timedelta(days=1)        
#        end_date = date.today()
#        formatted_date = start_date.strftime('%A, %B %d, %Y')        
#        report_title = 'Transactions Summary for Yesterday, ' + formatted_date
#    elif report == 'week':
#        d = date.today()
#        start_date = d - timedelta(days=d.weekday())        
#        end_date = date.today()
#        formatted_date = start_date.strftime('%A, %B %d, %Y')        
#        report_title = 'Transaction Summary for the Week Beginning ' + formatted_date
#    elif report == 'month':
#        start_date = date(date.today().year, date.today().month , 01)        
#        end_date = date.today()
#        formatted_date = start_date.strftime('%B, %Y')        
#        report_title = 'Transactions Summary for the Month of ' + formatted_date
#    elif report == 'year':
#        start_date = date(date.today().year, 01, 01)  
#        end_date = date.today() + timedelta(days=1)
#        formatted_date = start_date.strftime('%Y')        
#        report_title = 'Transaction Summary for Year of ' + formatted_date
#    elif report == 'custom':
#        start_date = date.today() - timedelta(days=1)        
#        end_date = date.today()
#        formatted_date = start_date.strftime('%A, %B %d, %Y')        
#        report_title = 'Transaction Summary from ' + formatted_date
#        report_title += 'to ' + end_date.strftime('%A, %B %d, %Y')
#
#    context['report_title'] = report_title
#    context['transactions'] = Transaction.objects.filter(date__range =
#                                                    (start_date, end_date),)
#    
#    return render_to_response('reporting/transactions_list.html', context,
#                                context_instance=RequestContext(request))
