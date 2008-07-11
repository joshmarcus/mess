from django.template import RequestContext
from django.shortcuts import render_to_response

def daily_report(request):
    """Page to reconcile the day's transactions."""
    context = {}
    return render_to_response('reporting/daily_report.html', context,
                                context_instance=RequestContext(request))

