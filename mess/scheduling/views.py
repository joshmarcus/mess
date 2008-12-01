import datetime

from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.views.generic.create_update import *
from django.contrib.auth.decorators import login_required


from mess.scheduling.models import *
from mess.scheduling.forms import *

#task crud
task_dict =  {
    'model': Task,
    'login_required': True,
}

def update_task(request, **kwargs):
    up_dict = dict(task_dict)
    up_dict.update(kwargs)
    return update_object(request, post_save_redirect=reverse('scheduling-schedule'), **up_dict)

def delete_task(request, **kwargs):
    del_dict = dict(task_dict)
    del_dict.update(kwargs)
    return delete_object(request, post_delete_redirect=reverse('scheduling-schedule'), **del_dict)

def add_task(request, task_id=None):
    context = {}

    if task_id == None:
        context = {
            'task_form': TaskForm(),
        }
    else:
        task = Task.objects.get(id__exact=task_id)
        context = {
            'task_form': TaskForm(instance=task),
            'task': task,
        }
    
    return render_to_response('scheduling/task_form.html', context,
                                context_instance=RequestContext(request))

def task_list(request, date=None):
    "return an html snippet listing tasks for the selected day"
    if date == None:
        date = datetime.date.today()
    else:
        year, month, day = date.split('-')
        date = datetime.date(int(year), int(month), int(day))
    
    context = {
        'tasks': Task.objects.filter(deadline__year=date.year, deadline__month=date.month, deadline__day=date.day)
    }
    return render_to_response('scheduling/snippets/task_list.html', context,
                                context_instance=RequestContext(request))
                                
def open_task_list(request, date=None):
    "return an html snippet listing all open tasks for the selected day"
    if date == None:
        date = datetime.date.today()
    else:
        year, month, day = date.split('-')
        date = datetime.date(int(year), int(month), int(day))
    
    context = {
        'tasks': Task.objects.filter(deadline__year=date.year, deadline__month=date.month, deadline__day=date.day)
    }
    return render_to_response('scheduling/snippets/open_task_list.html', context,
                                context_instance=RequestContext(request))

def open_task_list_month(request, date=None):
    "return an html snippet listing all days with open tasks for a specified month"
    if date == None:
        date = datetime.date.today()
    else:
        year, month = date.split('-')
        date = datetime.date(int(year), int(month))
    
    context = {
        'tasks': Task.objects.filter(deadline__year=date.year, deadline__month=date.month, member='null')
    }
    return render_to_response('scheduling/snippets/open_task_list_month.html', context,
                                context_instance=RequestContext(request))
        
def schedule(request):
    date = datetime.date.today()
    context = {
        'tasks': Task.objects.filter(deadline__year=date.year, deadline__month=date.month)
    }
    return render_to_response('scheduling/schedule.html', context,
                                context_instance=RequestContext(request))

def assign(request):
    date = datetime.date.today()
    context = {
        'tasks': Task.objects.filter(deadline__year=date.year, deadline__month=date.month)
    }
    return render_to_response('scheduling/assign.html', context,
                                context_instance=RequestContext(request))

# filter for date
def timecard(request):
    context = {
        'jobs': Job.objects.all()
    }
    return render_to_response('scheduling/timecard.html', context,
                                context_instance=RequestContext(request))    
def jobs(request):
    context = {
        'jobs': Job.objects.all()
    }
    return render_to_response('scheduling/jobs.html', context,
                                context_instance=RequestContext(request))

def job(request, job_id):
    context = {
        'jobs': Job.objects.filter(id=job_id)
    }
    return render_to_response('scheduling/jobs.html', context,
                                context_instance=RequestContext(request))

def job_edit(request, job_id=None):
    if job_id:
        job = get_object_or_404(Job, id=job_id)
    else:
        job = Job()
    is_errors = False
    ret_resp = HttpResponseRedirect(reverse('scheduling-jobs'))
    
    if request.method == 'POST':
        if 'cancel' in request.POST:
            return ret_resp

        job_form = JobForm(request.POST, instance=job)
        if job_form.is_valid():
            job_form.save()
            return ret_resp
        else:
            is_errors = True
    else:
        job_form = JobForm(instance=job)

    context = {
        'job': job,
        'is_errors': is_errors,
        'job_form': job_form,
        'add': job_id==None,
    }
    return render_to_response('scheduling/job_form.html', context,
                                context_instance=RequestContext(request))
