from datetime import date, timedelta
import time

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse

from mess.accounting import models as a_models
from mess.accounting.models import Transaction
from mess.membership import models as m_models
#from mess.accounting.models import get_credit_choices, get_debit_choices
#from mess.accounting.models import get_trans_total

from mess.utils.search import list_usernames_from_fullname

def find_dups(mems):
    uniqs = {}
    dups = []
    found_dups = {}
    for member in mems:
        fullname = member.user.get_full_name()
        if fullname in uniqs:
            dups.append(member)
            if fullname not in found_dups:
                dups.append(uniqs[fullname])
                found_dups[fullname] = 1
        else:
            uniqs[fullname] = member
    return dups

def anomalies(request):
    blips = 0
    report = ''
    mems = m_models.Member.objects.all()
    issues = [('Missing Firstname', mems.filter(user__first_name='Firstname')),
        ('Semicolon in Name', mems.filter(user__first_name__contains=';')),
        ('Comma in Name', mems.filter(user__first_name__contains=',')),
        ('Missing Lastname', mems.filter(user__last_name='Lastname')),
        ('Duplicate Name', find_dups(mems)),
        ]
    for issue, afflicteds in issues:
        report += '<h3>%s (%d members)</h3>\n' % (issue, len(afflicteds))
        blips += len(afflicteds)
        for m in afflicteds:
            report += '<a href="/membership/members/%s">%s</a> \
                (<a href="/membership/accounts/%s">%s</a>)<br>\n' % \
                (m.user.username, m, m.primary_account().id, m.primary_account())

    report = '<h1>Anomalies Report (%d blips)</h1>\n' % blips + report
    return HttpResponse(report)

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
    for type, name in a_models.PURCHASE_CHOICES:
        name = name.lower().replace(' ','_')
        total_name = 'total_' + name
        transactions = Transaction.objects.filter(
                timestamp__range=(start_date, end_date),
                purchase_type=type)
        context[name] = transactions
        context[total_name] = get_trans_total(transactions, 'purchase')
        context['total_credits'] += context[total_name]
    for type, name in a_models.PAYMENT_CHOICES:
        name = name.lower().replace(' ','_')
        total_name = 'total_' + name
        transactions = Transaction.objects.filter(
                timestamp__range=(start_date, end_date),
                payment_type=type)
        context[name] = transactions
        context[total_name] = get_trans_total(transactions, 'payment')
        context['total_debits'] += context[total_name]

    return render_to_response('reporting/transactions_summary.html', context,
            context_instance=RequestContext(request))


# helper functions below

def get_trans_total(trans, type='all'):
    total = 0
    if type == 'all' or type == 'purchase':
        for tran in trans:
            total += tran.purchase_amount
    if type == 'all' or type == 'payment':
        for tran in trans:
            total += tran.payment_amount
    return total

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
