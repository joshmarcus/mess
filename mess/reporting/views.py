from datetime import date

from django.template import RequestContext
from django.shortcuts import render_to_response

from mess.accounting.models import Transaction
from mess.accounting.models import get_credit_choices, get_debit_choices
from mess.accounting.models import get_trans_total

def daily_report(request):
    """Page to summerize the day's transactions."""
    context = {}
    context['page_name'] = 'Close Out'
    context['total_credits'] = 0
    context['total_debits'] = 0
    d = date.today()
    context['date'] = d.strftime('%A, %B %d, %Y')
    for type, name in get_credit_choices('Staff'):
        name = name.lower().replace(' ','_')
        total_name = 'total_' + name
        context[name] = Transaction.objects.filter(date__year = d.year,
                                                date__month = d.month,
                                                date__day = d.day,
                                                credit_type = type,)
        context[total_name] = get_trans_total(context[name], 'credit')
        context['total_credits'] += context[total_name]
    for type, name in get_debit_choices('Staff'):
        name = name.lower().replace(' ','_')
        total_name = 'total_' + name
        context[name] = Transaction.objects.filter(date__year = d.year,
                                                date__month = d.month,
                                                date__day = d.day,
                                                debit_type = type,)
        context[total_name] = get_trans_total(context[name], 'debit')
        context['total_debits'] += context[total_name]

    return render_to_response('reporting/daily_report.html', context,
                                context_instance=RequestContext(request))

