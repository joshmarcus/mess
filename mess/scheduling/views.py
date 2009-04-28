import datetime, time
from dateutil.relativedelta import relativedelta

#from django.conf import settings
#from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
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
    tasks = models.Task.objects.unassigned().filter(
            time__gte = firstday,
            time__lte = lastday
    )
    for task in tasks:
        datestr = task.time.strftime(format)
        days[datestr] = days.get(datestr, 0) + 1
    #for task in models.Task.recurring.unassigned():
    #    occur_times = task.get_occur_times(firstday, lastday)
    #    for occur_time in occur_times:
    #        datestr = occur_time.strftime(format)
    #        days[datestr] = days.get(datestr, 0) + 1
    return days
    
def unassigned_for_month(request, month):
    try:
#        date = datetime.datetime.strptime(month, "%Y-%m") Python 2.4 workaround
        date = datetime.datetime(*time.strptime(month, "%Y-%m")[0:5])
    except ValueError:
        raise Http404
    firstday = date + relativedelta(day=1)
    lastday = date + relativedelta(day=31)
    days = unassigned_days(firstday, lastday)
    return HttpResponse(simplejson.dumps(days))

@user_passes_test(lambda u: u.is_staff)
def task(request, task_id):
    task = get_object_or_404(models.Task, id=task_id)
#   date = str(task.time.date())
    return HttpResponseRedirect(reverse('scheduling-schedule', 
                    args=[task.time.date()])+'?jump_to_task_id='+str(task_id))

@user_passes_test(lambda u: u.is_staff)
def schedule(request, date=None):
    context = RequestContext(request)
    if date:
        try:
#            date = datetime.datetime.strptime(date, "%Y-%m-%d") Python 2.4 workaround
            date = datetime.datetime(*time.strptime(date, "%Y-%m-%d")[0:5])
        except ValueError:
            raise Http404
    else:
        today = datetime.date.today()
        # need datetime object for rrule, but datetime.today is, like, now
        date = datetime.datetime(today.year, today.month, today.day)
    add_task_form = forms.TaskForm(instance=models.Task(time=date), 
            prefix='add')
    add_recur_form = forms.RecurForm(prefix='recur-add')
    tasks = models.Task.objects.filter(time__year=date.year).filter(
            time__month=date.month).filter(time__day=date.day).order_by(
            'time', 'hours', 'job', '-recur_rule')
    prepared_tasks = []
    for index, task in enumerate(tasks):
        task.form = forms.TaskForm(instance=task, prefix=str(index))
        task.recur_form = forms.RecurForm(instance=task.recur_rule, 
                prefix='recur-%s' % index)
        prepared_tasks.append(task)

    if request.method == 'POST':
        if 'save-add' in request.POST:
            task_form = add_task_form = forms.TaskForm(request.POST, 
                    prefix='add')
            recur_form = add_recur_form = forms.RecurForm(request.POST, 
                    prefix='recur-add')
        else:
            task_index = request.POST.get('task-index')
            task = prepared_tasks[int(task_index)]
            if 'duplicate' in request.POST:
                task.excused = True
                task.save()
                task.duplicate()
                return HttpResponseRedirect(reverse('scheduling-schedule', 
                        args=[date.date()]))
            elif 'remove' in request.POST:
                if task.recur_rule:
                    future_tasks = task.recur_rule.task_set.filter(
                            time__gt=task.time)
                    for future_task in future_tasks:
                        future_task.delete()
                task.delete()
                return HttpResponseRedirect(reverse('scheduling-schedule', 
                        args=[date.date()]))
            task_form = task.form = forms.TaskForm(request.POST, 
                    instance=task, prefix=task_index)
            recur_form = task.recur_form = forms.RecurForm(request.POST, 
                    instance=task, prefix='recur-%s' % task_index)
        if task_form.is_valid() and recur_form.is_valid():
            task = task_form.save()
            if recur_form.changed_data:
                frequency = recur_form.cleaned_data['frequency']
                interval = recur_form.cleaned_data['interval']
                until = recur_form.cleaned_data['until']
                task.set_recur_rule(frequency, interval, until)
                task.update_buffer()
            return HttpResponseRedirect(reverse('scheduling-schedule', 
                    args=[date.date()]))

    # else... if request.method != POST
    elif request.GET.has_key('jump_to_task_id'):
        try:
            context['jump_to_task_id'] = int(request.GET['jump_to_task_id'])
        except:
            pass

    context['date'] = date
    a_day = datetime.timedelta(days=1)
    context['previous_date'] = date - a_day
    context['next_date'] = date + a_day
    firstday = date + relativedelta(day=1)
    lastday = date + relativedelta(day=31)
    context['cal_json']  = simplejson.dumps(unassigned_days(firstday, lastday))

    context['tasks'] = prepared_tasks
    context['add_task_form'] = add_task_form
    context['add_recur_form'] = add_recur_form
    # to include autocomplete js media files:
    context['form'] = {'media':add_task_form.media}
    template = loader.get_template('scheduling/schedule.html')
    return HttpResponse(template.render(context))

# filter for date
@user_passes_test(lambda u: u.is_staff)
def timecard(request, date=None):
    context = RequestContext(request)
    if date:
        try:
#            date = datetime.datetime.strptime(date, "%Y-%m-%d")  Python 2.4 workaround
            date = datetime.datetime(*time.strptime(date, "%Y-%m-%d")[0:5])
        except ValueError:
            raise Http404
    else:
        today = datetime.date.today()
        # need datetime object for rrule, but datetime.today is, like, now
        date = datetime.datetime(today.year, today.month, today.day)
# It seems our ordering was not deterministic enough, and that caused the 
# 'Task with this None already exists' if the request.POST and the queryset 
# ended up with different ordering.  Fixed by adding order_by 'id'.  -Paul
    tasks = models.Task.objects.filter(time__range=(
        datetime.datetime.combine(date, datetime.time.min), 
        datetime.datetime.combine(date, datetime.time.max))).exclude(
        account__isnull=True, excused=True).order_by('time', 'hours', 'job',
        '-recur_rule', 'id')
    if request.method == 'POST':
        formset = forms.TimecardFormSet(request.POST, request.FILES, 
                queryset=tasks)
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect(reverse('scheduling-timecard',
                   args=[date.date()]))
    else:
        formset = forms.TimecardFormSet(queryset=tasks)

    context['formset'] = formset
    context['date'] = date
    a_day = datetime.timedelta(days=1)
    context['previous_date'] = date - a_day
    context['next_date'] = date + a_day
    context['old_rotations'] = old_rotations(date)
    template = loader.get_template('scheduling/timecard.html')
    return HttpResponse(template.render(context))

def old_rotations(date):
    cycle_begin = datetime.datetime(2009,1,26)
    delta = (date - cycle_begin).days
    fourweek = 'ABCD'[int(delta/7) % 4]
    sixweek = 'EFGHIJ'[int(delta/7) % 6]
    eightweek = 'MNOPQRKL'[int(delta/7) % 8]
    return ', '.join([fourweek, sixweek, eightweek])

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

#def _task_template_save(proto_form, worker_formset):
#    task_template = proto_form.save(commit=False)
#    for form in worker_formset.forms:
#        #task_data = form.cleaned_data.copy()
#        #if not task_data['id']:
#        #    del task_data['id']
#        task = models.Task(**form.cleaned_data)
#        task.time = task_template.time
#        task.hours = task_template.hours
#        # TODO: set frequency and interval of recur_rule
#        #task.frequency = task_template.frequency
#        #task.interval = task_template.interval
#        task.job = task_template.job
#        task.save()
#
    # convert QuerySet to list for appending recurring tasks
    #task_list = list(tasks)
    #recurring_tasks = models.Task.recurring.all()
    #for task in recurring_tasks:
    #    occur_times = task.get_occur_times(date, date + a_day)
    #    for occur_time in occur_times:
    #        task_list.append(task)

    # group tasks by same job, time, and hours
    #task_groups = []
    #for task in tasks:
    #    group_found = False
    #    for group in task_groups:
    #        if (task.time == group[0] and task.hours == group[1] and 
    #                task.job == group[2] and task.recur_rule == group[3]):
    #            group[4].append(task)
    #            group_found = True
    #            continue
    #    if not group_found:
    #        task_groups.append((task.time, task.hours, task.job, 
    #                task.recur_rule, [task]))
    #task_groups.sort()

    # make it easier to get to things in the template
    #task_group_dicts = []
    #for index, group in enumerate(task_groups):
    #    tasks = []
    #    for task in group[4]:
    #        if task.member and task.account:
    #            tasks.append((task.member.user.get_full_name(), 
    #                    task.account.name, task))
    #        else:
    #            tasks.append((None, None, task))
    #    tasks.sort()
    #    tasks = [task[2] for task in tasks]
    #    first_task = tasks[0]
    #    form = forms.TaskForm(instance=first_task, prefix='%s' % index)
    #    task_dicts = []
    #    for task in tasks:
    #        if task.member and task.account:
    #            task_dicts.append({'taskid': task.id, 'member': task.member.id, 
    #                    'account': task.account.id})
    #        else:
    #            task_dicts.append({'taskid': task.id, 'member': '', 'account': ''})
    #    worker_formset = forms.WorkerFormSet(initial=task_dicts, 
    #            prefix='%s-worker' % index)
    #    group_dict = {'first_task': first_task, 'tasks': tasks, 'form': form,
    #            'worker_formset': worker_formset}
    #    task_group_dicts.append(group_dict)

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

