import datetime
from dateutil.relativedelta import *


from django.template import loader, RequestContext
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.views.generic.create_update import *
from django.contrib.auth.decorators import login_required
from django.utils import simplejson

from mess.scheduling import forms, models


#task crud
task_dict =  {
    'model': models.Task,
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
            'task_form': forms.TaskForm(),
        }
    else:
        task = models.Task.objects.get(id__exact=task_id)
        context = {
            'task_form': forms.TaskForm(instance=task),
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
        'tasks': models.Task.objects.filter(deadline__year=date.year, deadline__month=date.month, deadline__day=date.day)
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
        'tasks': models.Task.objects.filter(deadline__year=date.year, deadline__month=date.month, deadline__day=date.day)
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
        'tasks': models.Task.objects.filter(deadline__year=date.year, deadline__month=date.month, member='null')
    }
    return render_to_response('scheduling/snippets/open_task_list_month.html', context,
                                context_instance=RequestContext(request)
    )

def unassigned_days(firstday, lastday):
    'Pass in a range of days, get back a dict of days with count of unassigned tasks'
    days = {}

    tasks = models.Task.singles.unassigned().filter(
            time__gte = firstday,
            time__lte = lastday
    )

    for task in tasks:
        datestr = str(task.time.date())
        days[datestr] = days.get(datestr, 0) + 1

    for task in models.Task.recurring.unassigned():
        occur_times = task.get_occur_times(firstday, lastday)
        for occur_time in occur_times:
            datestr = str(occur_time.date())
            days[datestr] = days.get(datestr, 0) + 1

    return days
    

def unassigned_for_month(request, month):
    try:
        date = datetime.datetime.strptime(month, "%Y-%m")
    except ValueError:
        raise Http404
    
    firstday = date + relativedelta(day=1)
    lastday = date + relativedelta(day=31)
    
    days = unassigned_days(firstday, lastday)

    return HttpResponse(simplejson.dumps(days))
    

def schedule(request, date=None):
    context = RequestContext(request)
    if date:
        try:
            date = datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise Http404
    else:
        today = datetime.date.today()
        # need datetime object for rrule, but datetime.today is, like, now
        date = datetime.datetime(today.year, today.month, today.day)
    context['date'] = date
    a_day = datetime.timedelta(days=1)
    context['previous_date'] = date - a_day
    context['next_date'] = date + a_day
    tasks = models.Task.singles.filter(
            time__year=date.year).filter(time__month=date.month).filter(
            time__day=date.day)

    # convert QuerySet to list for appending recurring tasks
    task_list = list(tasks)
    recurring_tasks = models.Task.recurring.all()
    for task in recurring_tasks:
        occur_times = task.get_occur_times(date, date + a_day)
        for occur_time in occur_times:
            task_list.append(task)

    # group tasks by same job, time, and hours
    task_groups = []
    for task in task_list:
        group_found = False
        for group in task_groups:
            if (task.time.hour == group[0] and task.time.minute == group[1]
                    and task.hours == group[2] and task.job == group[3] and 
                    task.frequency == group[4] and task.deadline == group[5]):
                group[6].append(task)
                group_found = True
                continue
        if not group_found:
            task_groups.append((task.time.hour, task.time.minute, task.hours, 
                    task.job, task.frequency, task.deadline, [task]))
    task_groups.sort()

    # make it easier to get to things in the template
    task_group_dicts = []
    for group in task_groups:
        tasks = []
        for task in group[6]:
            if task.member and task.account:
                tasks.append((task.member.user.get_full_name(), 
                        task.account.name, task))
            else:
                tasks.append((None, None, task))
        tasks.sort()
        tasks = [task[2] for task in tasks]
        form = forms.TaskGroupForm(instance=tasks[0])
        worker_forms = [forms.WorkerForm(instance=task) for task in tasks]
        group_dict = {'proto': tasks[0], 'tasks': tasks, 'form': form,
                'worker_forms': worker_forms}
        task_group_dicts.append(group_dict)

    context['task_groups'] = task_group_dicts
    template = loader.get_template('scheduling/schedule.html')
    return HttpResponse(template.render(context))

def assign(request):
    date = datetime.date.today()
    context = {
        'tasks': models.Task.objects.filter(deadline__year=date.year, deadline__month=date.month)
    }
    return render_to_response('scheduling/assign.html', context,
                                context_instance=RequestContext(request))

# filter for date
def timecard(request):
    context = {
        'jobs': models.Job.objects.all()
    }
    return render_to_response('scheduling/timecard.html', context,
                                context_instance=RequestContext(request))    
def jobs(request):
    context = {
        'jobs': models.Job.objects.all()
    }
    return render_to_response('scheduling/jobs.html', context,
                                context_instance=RequestContext(request))

def job(request, job_id):
    context = {
        'jobs': models.Job.objects.filter(id=job_id)
    }
    return render_to_response('scheduling/jobs.html', context,
                                context_instance=RequestContext(request))

def job_edit(request, job_id=None):
    if job_id:
        job = get_object_or_404(models.Job, id=job_id)
    else:
        job = models.Job()
    is_errors = False
    ret_resp = HttpResponseRedirect(reverse('scheduling-jobs'))
    
    if request.method == 'POST':
        if 'cancel' in request.POST:
            return ret_resp

        job_form = forms.JobForm(request.POST, instance=job)
        if job_form.is_valid():
            job_form.save()
            return ret_resp
        else:
            is_errors = True
    else:
        job_form = forms.JobForm(instance=job)

    context = {
        'job': job,
        'is_errors': is_errors,
        'job_form': job_form,
        'add': job_id==None,
    }
    return render_to_response('scheduling/job_form.html', context,
                                context_instance=RequestContext(request))
