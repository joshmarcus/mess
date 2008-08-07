import datetime

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.views.generic.create_update import *

from mess.scheduling.models import *

#task crud
task_dict =  {
    'model': Task,
    'login_required': True,
}

def add_task(request, **kwargs):
    add_dict = dict(task_dict)
    add_dict.update(kwargs)
    return create_object(request, post_save_redirect=reverse("staff-schedules"), **add_dict)

def update_task(request, **kwargs):
    up_dict = dict(task_dict)
    up_dict.update(kwargs)
    return update_object(request, post_save_redirect=reverse("staff-schedules"), **up_dict)

def delete_task(request, **kwargs):
    del_dict = dict(task_dict)
    del_dict.update(kwargs)
    return delete_object(request, post_delete_redirect=reverse("staff-schedules"), **del_dict)

def task_list(request, date=None):
    if date == None:
        date = datetime.date.today()
    else:
        year, month, day = date.split('-')
        date = datetime.date(int(year), int(month), int(day))
    
    context = {
        'tasks': Task.objects.filter(deadline__year=date.year, deadline__month=date.month, deadline__day=date.day)
    }
    return render_to_response('scheduling/task_list.html', context,
                                context_instance=RequestContext(request))
        
def monthly(request):
    date = datetime.date.today()

    context = {
        'tasks': Task.objects.filter(deadline__year=date.year, deadline__month=date.month)
    }
    return render_to_response('scheduling/monthly.html', context,
                                context_instance=RequestContext(request))

