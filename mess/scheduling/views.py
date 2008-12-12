import datetime
from dateutil.relativedelta import relativedelta

#from django.conf import settings
#from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import loader, RequestContext
from django.utils import simplejson
#from django.views.generic.create_update import *

from mess.scheduling import forms, models


def unassigned_days(firstday, lastday):
    """
    Pass in a range of days, get back a dict of days with count of 
    unassigned tasks
    """
    days = {}
    format = "%m/%d/%Y"
    tasks = models.Task.singles.unassigned().filter(
            time__gte = firstday,
            time__lte = lastday
    )
    for task in tasks:
        datestr = task.time.strftime(format)
        days[datestr] = days.get(datestr, 0) + 1
    for task in models.Task.recurring.unassigned():
        occur_times = task.get_occur_times(firstday, lastday)
        for occur_time in occur_times:
            datestr = occur_time.strftime(format)
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
    
@user_passes_test(lambda u: u.is_staff)
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
    add_form = forms.TaskForm(instance=models.Task(time=date))
    add_worker_formset = forms.WorkerAddFormSet(prefix='worker')
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
                    task.frequency == group[4]):
                group[5].append(task)
                group_found = True
                continue
        if not group_found:
            task_groups.append((task.time.hour, task.time.minute, task.hours, 
                    task.job, task.frequency, [task]))
    task_groups.sort()

    # make it easier to get to things in the template
    task_group_dicts = []
    for index, group in enumerate(task_groups):
        tasks = []
        for task in group[5]:
            if task.member and task.account:
                tasks.append((task.member.user.get_full_name(), 
                        task.account.name, task))
            else:
                tasks.append((None, None, task))
        tasks.sort()
        tasks = [task[2] for task in tasks]
        first_task = tasks[0]
        form = forms.TaskForm(instance=first_task, prefix='%s' % index)
        task_dicts = []
        for task in tasks:
            if task.member and task.account:
                task_dicts.append({'id': task.id, 'member': task.member.id, 
                        'account': task.account.id})
            else:
                task_dicts.append({'id': task.id, 'member': '', 'account': ''})
        worker_formset = forms.WorkerFormSet(initial=task_dicts, 
                prefix='%s-worker' % index)
        group_dict = {'first_task': first_task, 'tasks': tasks, 'form': form,
                'worker_formset': worker_formset}
        task_group_dicts.append(group_dict)

    firstday = date + relativedelta(day=1)
    lastday = date + relativedelta(day=31)
    context['cal_json']  = simplejson.dumps(unassigned_days(firstday, lastday))
    
    if request.method == 'POST':
        if 'save-add' in request.POST:
            add_form = forms.TaskForm(request.POST)
            add_worker_formset = forms.WorkerAddFormSet(request.POST, prefix='worker')
            if add_form.is_valid() and add_worker_formset.is_valid():
                _task_template_save(add_form, add_worker_formset.forms)
                return HttpResponseRedirect(reverse('scheduling-schedule', 
                        args=[date.date()]))
        else:
            group_index = request.POST.get('group-index')
            group_index_int = int(group_index)
            edit_form = forms.TaskForm(request.POST, instance=task_group_dicts[group_index_int]['first_task'], prefix=group_index)
            edit_worker_formset = forms.WorkerFormSet(request.POST, prefix=group_index + '-worker')
            if edit_form.is_valid() and edit_worker_formset.is_valid():
                pass
            else:
                this_dict = task_group_dicts[int(group_index)]
                this_dict['form'] = edit_form
                this_dict['worker_formset'] = edit_worker_formset

    add_form.add = True
    context['task_groups'] = task_group_dicts
    context['add_form'] = add_form
    context['add_worker_formset'] = add_worker_formset
    template = loader.get_template('scheduling/schedule.html')
    return HttpResponse(template.render(context))

def _task_template_save(proto_form, worker_forms):
    task_template = proto_form.save(commit=False)
    for form in worker_forms:
        task = models.Task(**form.cleaned_data)
        task.time = task_template.time
        task.hours = task_template.hours
        task.frequency = task_template.frequency
        task.interval = task_template.interval
        task.job = task_template.job
        task.save()

def worker_form(request):
    context = RequestContext(request)
    index = request.GET.get('index')
    if index:
        form = forms.WorkerForm(prefix='%s-%s' % ('worker', index))
    else:
        form = forms.WorkerForm()
    context['form'] = form
    template = loader.get_template('scheduling/snippets/worker_form.html')
    return HttpResponse(template.render(context))

# filter for date
@user_passes_test(lambda u: u.is_staff)
def timecard(request):
    context = {
        'jobs': models.Job.objects.all()
    }
    return render_to_response('scheduling/timecard.html', context,
                                context_instance=RequestContext(request))    

@user_passes_test(lambda u: u.is_staff)
def jobs(request):
    context = {
        'jobs': models.Job.objects.all()
    }
    return render_to_response('scheduling/jobs.html', context,
                                context_instance=RequestContext(request))

@user_passes_test(lambda u: u.is_staff)
def job(request, job_id):
    context = {
        'jobs': models.Job.objects.filter(id=job_id)
    }
    return render_to_response('scheduling/jobs.html', context,
                                context_instance=RequestContext(request))

@user_passes_test(lambda u: u.is_staff)
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


# unused below

#def assign(request):
#    date = datetime.date.today()
#    context = {
#        'tasks': models.Task.objects.filter(deadline__year=date.year, deadline__month=date.month)
#    }
#    return render_to_response('scheduling/assign.html', context,
#                                context_instance=RequestContext(request))

#task crud
#task_dict =  {
#    'model': models.Task,
#    'login_required': True,
#}
#
#def update_task(request, **kwargs):
#    up_dict = dict(task_dict)
#    up_dict.update(kwargs)
#    return update_object(request, post_save_redirect=reverse('scheduling-schedule'), **up_dict)
#
#def delete_task(request, **kwargs):
#    del_dict = dict(task_dict)
#    del_dict.update(kwargs)
#    return delete_object(request, post_delete_redirect=reverse('scheduling-schedule'), **del_dict)
#
#def add_task(request, task_id=None):
#    context = {}
#
#    if task_id == None:
#        context = {
#            'task_form': forms.TaskForm(),
#        }
#    else:
#        task = models.Task.objects.get(id__exact=task_id)
#        context = {
#            'task_form': forms.TaskForm(instance=task),
#            'task': task,
#        }
#    
#    return render_to_response('scheduling/task_form.html', context,
#                                context_instance=RequestContext(request))
#
#def task_list(request, date=None):
#    "return an html snippet listing tasks for the selected day"
#    if date == None:
#        date = datetime.date.today()
#    else:
#        year, month, day = date.split('-')
#        date = datetime.date(int(year), int(month), int(day))
#    
#    context = {
#        'tasks': models.Task.objects.filter(deadline__year=date.year, deadline__month=date.month, deadline__day=date.day)
#    }
#    return render_to_response('scheduling/snippets/task_list.html', context,
#                                context_instance=RequestContext(request))
#                                
#def open_task_list(request, date=None):
#    "return an html snippet listing all open tasks for the selected day"
#    if date == None:
#        date = datetime.date.today()
#    else:
#        year, month, day = date.split('-')
#        date = datetime.date(int(year), int(month), int(day))
#    
#    context = {
#        'tasks': models.Task.objects.filter(deadline__year=date.year, deadline__month=date.month, deadline__day=date.day)
#    }
#    return render_to_response('scheduling/snippets/open_task_list.html', context,
#                                context_instance=RequestContext(request))
#
#def open_task_list_month(request, date=None):
#    "return an html snippet listing all days with open tasks for a specified month"
#    if date == None:
#        date = datetime.date.today()
#    else:
#        year, month = date.split('-')
#        date = datetime.date(int(year), int(month))
#    
#    context = {
#        'tasks': models.Task.objects.filter(deadline__year=date.year, deadline__month=date.month, member='null')
#    }
#    return render_to_response('scheduling/snippets/open_task_list_month.html', context,
#                                context_instance=RequestContext(request)
#    )

