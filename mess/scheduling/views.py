import datetime, time, calendar
from dateutil.relativedelta import relativedelta

#from django.conf import settings
#from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import loader, RequestContext, Context
from django.utils import simplejson
import django.views.decorators.vary as vary

from mess.scheduling import forms, models
from mess.membership import forms as m_forms
from mess.membership import models as m_models

today = datetime.date.today()
todaytime = datetime.datetime(today.year,today.month,today.day)

@login_required
def myschedule(request):
    member = request.user.get_profile()
    account = member.get_primary_account()
    if request.method == 'POST' and request.POST.get('action') == 'Sign me up!':
        shift = get_object_or_404(models.Task, id=request.POST.get('task'))
        assert shift.member is None and shift.account is None
        if shift.time < todaytime + datetime.timedelta(11):
            return HttpResponse('Sorry, online signup is only available at least 11 days in advance.  You may still be able to sign up for this shift by going to the co-op.')
        if shift.recur_rule:
            shift = shift.excuse_and_duplicate()  # one-time fill
        shift.member = member
        shift.account = account
        shift.makeup = True
        shift.save()
    account_shifts = account.task_set.filter(
                     time__range=(today,today+datetime.timedelta(180)))
    my_shift = member.regular_shift()
    if my_shift:
        similar_assigned = models.Task.objects.filter(job=my_shift.job,
                           recur_rule__isnull=False,
                           time__range=(today,today+datetime.timedelta(42)),
                           hours=my_shift.hours,
                           member__isnull=False)
    unassigned = models.Task.objects.filter(member__isnull=True,
                 excused=False,
                 time__range=(today,today+datetime.timedelta(20)))
    return render_to_response('scheduling/myschedule.html', locals(),
                              context_instance=RequestContext(request))

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

def task(request, task_id):
    task = get_object_or_404(models.Task, id=task_id)
#   date = str(task.time.date())
    return HttpResponseRedirect(reverse('scheduling-schedule', 
                    args=[task.time.date()])+'?jump_to_task_id='+str(task_id))

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
    add_time = date + datetime.timedelta(hours=9)
    add_task_form = forms.TaskForm(instance=models.Task(time=add_time), 
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

def old_rotations(date, interval=None):
    cycle_begin = datetime.datetime(2009,1,26)
    delta = (date - cycle_begin).days
    fourweek = 'ABCD'[int(delta/7) % 4]
    sixweek = 'EFGHIJ'[int(delta/7) % 6]
    eightweek = 'MNOPQRKL'[int(delta/7) % 8]
    if interval == 4:
        return fourweek
    elif interval == 6:
        return sixweek
    else:
        return ', '.join([fourweek, sixweek, eightweek])

@login_required
def rotation(request):
    """
    Print listings of shifts according to rotation cycles.
    We'll assume a shift is permanent if it's scheduled 10 rotations ahead.
    We try to match each 4-week shift to an 'ideal' slot on week of 1990-01-01.
    I'm hard-coding pagebreaks because page-break-inside:avoid; doesn't work.
    """ 
    context = RequestContext(request)
    horizon = 10
    rotationtables = []

    # get four-week rotations, idealizing them
    for weekday in range(0,7):
        table = {'freq':4, 'weekday':weekday, 'cycles':[], 
                 'dayname':calendar.day_name[weekday], 'pagebreakafter':True}
        table['idealdate'] = idealdate = datetime.date(1990, 1, 1+weekday)
        table['ideals'] = models.Task.objects.filter(time__range=(
                datetime.datetime.combine(idealdate, datetime.time.min),
                datetime.datetime.combine(idealdate, datetime.time.max)))
        for cycle in range(4):
            column = cyclecolumn(4, weekday, cycle)
            idealize(column['shifts'], table['ideals'])
            table['cycles'].append(column)
        rotationtables.append(table)

    # get six-week cashier rotations
    for weekday in range(0,7):
        table = {'freq':6, 'weekday':weekday, 'cycles':[], 'cashier6':True,
                 'dayname':calendar.day_name[weekday]}
        if weekday in [2,4,6]:
            table['pagebreakafter'] = True
        for cycle in range(6):
            table['cycles'].append(cyclecolumn(6, weekday, cycle, cashieronly=True))
        rotationtables.append(table)

    # get dancer shifts, idealizing them
    table = {'freq':4, 'dayname':'Dancer (by Sunday)', 
             'dancer':True, 'cycles':[]}
    table['idealdate'] = idealdate = datetime.date(1990, 1, 8)
    table['ideals'] = models.Task.objects.filter(time__range=(
                datetime.datetime.combine(idealdate, datetime.time.min),
                datetime.datetime.combine(idealdate, datetime.time.max)))
    for cycle in range(4):
        column = cyclecolumn(4, 6, cycle, getdancers=True)
        idealize(column['shifts'], table['ideals'])
        table['cycles'].append(column)
    rotationtables.append(table)

    context['rotationtables'] = rotationtables
    template = loader.get_template('scheduling/rotation.html')
    return HttpResponse(template.render(context))

def cyclecolumn(freq, weekday, cycle, getdancers=False, cashieronly=False):
    horizon = 7
    cycle_begin = datetime.datetime(2009,1,26)
    today = datetime.date.today()
    first = cycle_begin + datetime.timedelta(days=weekday+7*cycle)
    while first.date() < today:
        first += datetime.timedelta(days=7*freq)
    column = {}
    column['dates'] = [first + datetime.timedelta(days=7*freq*i)
        for i in range(horizon)]
    if freq == 4:
        column['letter'] = 'ABCD'[cycle]
    elif freq == 6:
        column['letter'] = 'EFGHIJ'[cycle]
    lastdate = (column['dates'][-1]).date()
    shifts = models.Task.objects.filter(time__range=(
              datetime.datetime.combine(lastdate, datetime.time.min),
              datetime.datetime.combine(lastdate, datetime.time.max)),
              recur_rule__interval=freq, recur_rule__frequency='w',)
    if getdancers:
        shifts = shifts.filter(job__name__icontains='dancer')
    else:
        shifts = shifts.exclude(job__name__icontains='dancer')
    if cashieronly:
        shifts = shifts.filter(job__name='Cashier')
    column['shifts'] = shifts.order_by('time','job')
    return column

def idealize(actualshifts, idealshifts):
    """
    Append the one best actual shift (or none) to each idealshift.actuals array
    Mark actual shifts as .idealized=True.
    We want to select the best matches, for example:
          ideal(9am)---actual(10am)    ideal(2pm)---actual(3pm)
          ideal(9am)---actual(10am)    ideal(2pm)-----None
          ideal(9am)---actual(10am)       None------actual(3pm)
          ideal(9am)-----None          ideal(2pm)---actual(3pm)
       but still match:     ideal(9am)---actual(3pm)
    To approximate this, we do several passes with increasing tolerance. 
    """
    for ideal in idealshifts:
        try:
            ideal.actuals.append(None)
        except AttributeError:
            ideal.actuals = [None]
        if actualshifts:
            ideal.actualizeddatetime = datetime.datetime.combine(
                    actualshifts[0].time.date(), 
                    ideal.time.time())
    for tolerance_hours in [0, 1, 4, 16]:
        tolerance = datetime.timedelta(hours=tolerance_hours)
        for ideal in idealshifts:
            if ideal.actuals[-1]:   # already matched on better tolerance
                continue
            for actual in actualshifts:
                if hasattr(actual, 'idealized'):
                    continue
                if actual.job != ideal.job:
                    continue
                timediff = abs(ideal.actualizeddatetime - actual.time)
                if timediff <= tolerance:
                    ideal.actuals[-1] = actual
                    actual.idealized = True
                    actual.timediff = timediff.seconds
                    break

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

def reminder(request, date):
    " send email reminder to all scheduled workers for this date "
    from django.core.mail import send_mail
    date = datetime.date(*time.strptime(date, "%Y-%m-%d")[:3])
    previous_date = date - datetime.timedelta(1)
    next_date = date + datetime.timedelta(1)
    tasks = models.Task.objects.filter(
            time__range=(date, date+datetime.timedelta(1)),
            member__isnull=False)
    noemail = tasks.filter(member__emails__isnull=True)
    tasks = tasks.filter(member__emails__isnull=False).distinct()
    message_template = loader.get_template('scheduling/reminder_mail.html')
    messages = []
    for task in tasks:
        message = message_template.render(Context({'task':task}))
        messages.append(unicode(message))
        if request.method == 'POST':
            (to, subject, message) = message.split('\n', 2)
            to = to.split(' ', 1)[1]
            subject = subject.split(' ', 1)[1]
            send_mail(subject, message, None, [to])
    return render_to_response('scheduling/reminder.html', locals(),
                                context_instance=RequestContext(request))

@login_required
def switch(request):
    original = models.Task.objects.get(id=request.GET['original'])
    if original.member is None or ((original.member.user != request.user)
                                   and not request.user.is_staff):
        return HttpResponse('Sorry.  You are not assigned to that task.')
    if original.makeup:
        return HttpResponse('Sorry.  Cannot switch a make-up shift.')
    SOONEST_SWITCH = datetime.timedelta(11)
    earliest_switch = datetime.datetime.now() + SOONEST_SWITCH
    if original.time < earliest_switch:
        return HttpResponse('Sorry.  Cannot switch shifts within %s' % SOONEST_SWITCH)
    if request.method == 'POST':
        switch = models.Task.objects.get(id=request.POST['task'])
        if switch.member or switch.account:
            return HttpResponse('Sorry.  Switch task is already assigned.')
        if switch.recur_rule:
            switch = switch.excuse_and_duplicate()  # one-time fill
        original.excuse_and_duplicate()
        switch.member = original.member
        switch.account = original.account
        switch.makeup = True
        switch.save()
        return HttpResponseRedirect(reverse('myschedule'))
    form = forms.PickTaskForm()
    # require switched task to be sooner than original.
    # try to switch to one-time task of same job.
    possible_switches = models.Task.objects.filter(
                time__range=(earliest_switch, original.time),
                hours=original.hours, job=original.job, excused=False,
                account__isnull=True, member__isnull=True, 
                recur_rule__isnull=True)
    # else try to switch to one-time task of any job.
    if possible_switches.count() == 0:
        possible_switches = models.Task.objects.filter(
                time__range=(earliest_switch, original.time),
                hours=original.hours, excused=False,
                account__isnull=True, member__isnull=True,
                recur_rule__isnull=True)
    # else try to create one-time fill within next 4 weeks
    if possible_switches.count() == 0:
        final_time_for_onetimefill = min(original.time, 
                todaytime + datetime.timedelta(28))
        possible_switches = models.Task.objects.filter(
                time__range=(earliest_switch, final_time_for_onetimefill),
                hours=original.hours, excused=False,
                account__isnull=True, member__isnull=True)
    form.fields['task'].queryset = possible_switches[:10]
    return render_to_response('scheduling/switch.html', locals(),
                              context_instance=RequestContext(request))

def swap(request):
    """ 
    two members swap shifts (one-time), and tell a staff person 
    uses member.remove_from_shifts to break recur_rules where needed
    """
    original = models.Task.objects.get(id=request.GET['original'])
    if request.method == 'POST':
        swap = models.Task.objects.get(id=request.POST['task'])
        DO_IT_RIGHT = False
        if DO_IT_RIGHT: 
            duporiginal = original.excuse_and_duplicate()
            duporiginal.account = swap.account
            duporiginal.member = swap.member
            duporiginal.save()
            dupswap = swap.excuse_and_duplicate()
            dupswap.account = original.account
            dupswap.member = original.member
            dupswap.save()
        else: # Do it wrong, breaking the recur_rules into halves
            original_account = original.account
            original_member = original.member
            original_member.remove_from_shifts(original.time.date(), 
                            original.time.date()+datetime.timedelta(1))
            swap_account = swap.account
            swap_member = swap.member
            swap_member.remove_from_shifts(swap.time.date(), 
                        swap.time.date()+datetime.timedelta(1))
            original.account = swap_account
            original.member = swap_member
            original.recur_rule = None
            original.save()
            swap.account = original_account
            swap.member = original_member
            swap.recur_rule = None
            swap.save()
        return HttpResponseRedirect(reverse('scheduling-schedule', 
                                    args=[original.time.date()]))
    if 'member' in request.GET:   # member to swap with
        swap_member = m_models.Member.objects.get(id=request.GET['member'])
        form = forms.PickTaskForm()
        form.fields['task'].queryset = models.Task.objects.filter(
                   member=swap_member, 
                   time__range=(today - datetime.timedelta(7),
                                today + datetime.timedelta(180)))
        form.fields['task'].initial = form.fields['task'].queryset[0].id
    else:
        form = m_forms.PickMemberForm()
    return render_to_response('scheduling/swap.html', locals(),
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

