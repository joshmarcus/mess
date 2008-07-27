from datetime import date, timedelta

from django.template import RequestContext
from django.shortcuts import render_to_response

from mess.accounting.models import Transaction
from mess.accounting.models import get_credit_choices, get_debit_choices
from mess.accounting.models import get_trans_total


def transaction_report(request,
                start_date=date(1900, 01, 01),
                end_date=date.today()):
    """View to summerize transactions by type."""
    context = {}
    context['page_name'] = 'Transaction Summaries'
    context['total_credits'] = 0
    context['total_debits'] = 0
    d = date.today()
    context['date'] = d.strftime('%A, %B %d, %Y')
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

