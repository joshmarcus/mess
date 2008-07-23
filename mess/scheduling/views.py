from datetime import datetime

from django.template import RequestContext
from django.shortcuts import render_to_response

from mess.scheduling.models import *

def monthly(request, month=None):
    if month == None:
        month = datetime.month
    
    context = {
        'tasks': Task.objects.all()
    }
    return render_to_response('scheduling/monthly.html', context,
                                context_instance=RequestContext(request))

