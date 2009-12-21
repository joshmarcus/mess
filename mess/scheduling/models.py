import datetime
from dateutil import rrule

from django.db import models
from django.template import loader, Context
from django.utils.safestring import mark_safe
from mess.membership.models import Account, Member
from mess.membership import models as m_models

today = datetime.date.today()
todaytime = datetime.datetime(today.year, today.month, today.day)

JOB_TYPES = (
    ('s','Staff'),
    ('p','Paid'),
    ('m','Member'),
)
FREQUENCIES = (
    ('d', 'Daily'),
    ('w', 'Weekly'),
    ('m', 'Monthly'),
)

class Skill(models.Model):
    """
    Skills needed to perform jobs
    """
    name = models.CharField(max_length=100, unique=True)
    
    def __unicode__(self):
        return self.name

class Job(models.Model):
    """
    Job description / title
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=1, choices=JOB_TYPES, default='m')
    deadline = models.BooleanField()
    freeze_days = models.IntegerField(default=7)
    hours_multiplier = models.IntegerField(default=1)
    skills_required = models.ManyToManyField(Skill, blank=True, 
            related_name='required_by')
    skills_trained = models.ManyToManyField(Skill, blank=True, 
            related_name='trained_by')

    def __unicode__(self):
        return self.name

    def is_dancer(self):
        return self.name[:4].lower() == 'danc'
    
    class Meta:
        ordering = ['name']


class RecurRule(models.Model):
    # use task.time for start
    #start = models.DateTimeField()
    frequency = models.CharField(max_length=1, choices=FREQUENCIES, blank=True)
    interval = models.PositiveIntegerField(blank=True)
    until = models.DateTimeField(null=True, blank=True)


class Exclusion(models.Model):
    date = models.DateTimeField()
    recur_rule = models.ForeignKey(RecurRule)


class TaskManager(models.Manager):
    'Custom manager to add extra methods'
    def unassigned(self):
        return self.filter(models.Q(member=None) | models.Q(account=None))

class Task(models.Model):
    """
    A task is a scheduled occurrence of a job.  The time is a start time 
    unless deadline is checked for the related job.
    """
    job = models.ForeignKey(Job)
    time = models.DateTimeField()
    hours = models.DecimalField(max_digits=4, decimal_places=2)
    note = models.TextField(blank=True)

    member = models.ForeignKey(Member, null=True, blank=True)
    account = models.ForeignKey(Account, null=True, blank=True)

    # hours_worked:  None = not entered   0 = did not work
    hours_worked = models.DecimalField(max_digits=4, decimal_places=2, 
            null=True, blank=True)
    excused = models.BooleanField()
    makeup = models.BooleanField()
    banked = models.BooleanField()

    recur_rule = models.ForeignKey(RecurRule, null=True, blank=True)

    objects = TaskManager()
    
    class Meta:
        ordering = ['time', 'hours', 'job']

    def __unicode__(self):
        try:
            return u'%s, %s %sh, %s (%s)' % (self.job, 
                self.time.strftime('%Y-%m-%d %I:%M%P'), self.hours,
                self.member.user.first_name, self.account)
        except AttributeError:
            return u'%s, %s %sh' % (self.job, 
                self.time.strftime('%Y-%m-%d %I:%M%P'), self.hours)

    def get_absolute_url(self):
        return '/scheduling/task/%s' % self.id

    def get_switch_url(self):
        return '/scheduling/switch/?original=%s' % self.id

    def after_printing_horizon(self):
        return bool(self.time > todaytime + datetime.timedelta(11))

    def html_display(self):
        template = loader.get_template('scheduling/snippets/task.html')
        if self.time < todaytime:
            datehorizon = 'other'
        elif self.time < todaytime + datetime.timedelta(180):
            datehorizon = 'shortterm'
        else:
            datehorizon = 'other'
        task = self
        return template.render(Context(locals()))

    @property
    def assigned(self):
        return bool(self.member and self.account)

    @property
    def unexcused(self):
        return (self.hours_worked == 0 and not self.excused)

    @property
    def workflag(self):
        flag = ''
        if self.excused:
            flag += 'excused '
        elif self.unexcused:
            flag += 'unexcused '
        if self.makeup:
            flag += 'makeup '
        if self.banked:
            flag += 'banked '
        return flag.strip()
        # possible values: '', 'excused', 'excusedmakeup', 'excusedbanked', 'excusedmakeupbanked', 'unexcused', 'unexcusedmakeup', 'unexcusedbanked', 'unexcusedmakeupbanked', 'makeup', 'banked', 'makeupbanked'

    @property
    def simple_workflag(self):
        if 'unexcused' in self.workflag:
            return 'unexcused'
        elif ' ' in self.workflag:
            return 'complex-workflag'
        elif self.workflag != '':
            return self.workflag
        elif self.hours_worked:
            return 'worked'
        else:
            return 'scheduled'

    @property
    # this returns things like Y2 or EM3 or UB2
    def abbr_workflag(self):
        if self.hours_worked:   # gt 0
            yeu = 'Y'
            hrs = self.hours_worked
        else:
            hrs = self.hours
            if self.excused:
                yeu = 'E'
            elif self.hours_worked == 0:
                yeu = 'U'
            else:
                yeu = '_'
        mb = ''
        if self.makeup:
            mb += 'M'
        if self.banked:
            mb += 'B'
        if int(hrs) == hrs:
            hrs = str(int(hrs))
        else:
            hrs = str(float(hrs))
        return yeu + mb + hrs

    @property
    def timecard_submitted(self):
        return (self.hours_worked is not None)

    def get_end(self):
        delta_hours = datetime.timedelta(hours=float(self.hours))
        end = self.time + delta_hours
        return end

    def new_date(self):
        '''
        If they have 4 or more past shifts that they actually did this year,
        then they're no longer new.  Except if it's a cashier, then the past
        shifts have to be cashiering shifts.
        '''
        if self.member:
            trainingjobs = ['Orientation Attendee','Shadow Cashier',
                            'Cashier Training Attendee']
            oldshifts = self.member.task_set.filter(time__lte=self.time,
                time__gt=datetime.date.today() - datetime.timedelta(365),
                hours_worked__gt=0).exclude(job__name__in=trainingjobs)
            if self.job.name == 'Cashier':
                oldshifts = oldshifts.filter(job__name=self.job.name)
                # FIXME only enough time for 2 past cashier shifts...
                # remove this line in October 2009:
                if len(oldshifts) >= 2: return
            if len(oldshifts) == 0:
                return self.time
            if len(oldshifts) < 4:
                return oldshifts[0].time

    def time_minus_six_days(self):
        return self.time - datetime.timedelta(6)

    def get_next_shift(self):
        if self.recur_rule:
            future_tasks = self.recur_rule.task_set.filter(time__gt=self.time)
            if future_tasks:
                next_task = future_tasks.order_by('time')[0]
                return next_task.time

    def set_recur_rule(self, frequency, interval, until):
        exclusions = []
        if self.recur_rule:
            recur_tasks = self.recur_rule.task_set.all()
            # delete all future tasks
            future_tasks = recur_tasks.filter(time__gt=self.time)
            for task in future_tasks:
                task.delete()
            # set current recur_rule to end on previous task if there is one
            past_tasks = recur_tasks.filter(time__lt=self.time).order_by(
                    '-time')
            if past_tasks:
                previous_task = past_tasks[0]
                self.recur_rule.until = previous_task.time
                self.recur_rule.save()
            exclusions = self.recur_rule.exclusion_set.all()
        recur_rule = RecurRule(frequency=frequency, interval=interval, 
                until=until)
        recur_rule.save()
        for exclusion in exclusions:
            exclusion.recur_rule = recur_rule
        self.recur_rule = recur_rule
        self.save()

    def duplicate_recur_rule(self):
        new_rule = RecurRule(frequency=self.recur_rule.frequency, 
                             interval=self.recur_rule.interval,
                             until=self.recur_rule.until)
        new_rule.save()
        return new_rule

    def exclude_from_recur_rule(self):
        exclude_date = Exclusion(date=self.time, recur_rule=self.recur_rule)
        exclude_date.save()
        self.recur_rule = None
        self.save()

    def update_buffer(self):
        """Update the 2-year date buffer."""
        if not self.recur_rule:
            return
        frequency = getattr(rrule, 
                self.recur_rule.get_frequency_display().upper())
        today = datetime.datetime.today()
        two_years_hence = today + datetime.timedelta(731)
        until = self.recur_rule.until or two_years_hence
        recur = rrule.rrule(frequency, dtstart=self.time, 
                interval=self.recur_rule.interval, until=until)
        recur_set = rrule.rruleset()
        recur_set.rrule(recur)
        for exclusion in self.recur_rule.exclusion_set.all():
            recur_set.exdate(exclusion.date)
        existing_tasks = Task.objects.filter(recur_rule=self.recur_rule)
        existing_dates = [task.time for task in existing_tasks]
        for task_date in recur_set:
            # don't re-create existing tasks
            if task_date in existing_dates:
                continue
            task = Task(job=self.job, time=task_date, hours=self.hours,
                    member=self.member, account=self.account, 
                    recur_rule=self.recur_rule)
            task.save()

    def duplicate(self):
        new_task = Task(job=self.job, time=self.time, hours=self.hours)
        new_task.save()
        return new_task

    def excuse_and_duplicate(self):
        ''' 
        Assigned shift: excuses member, duplicates shift for fill
        Unassigned shift: marks "excused", duplicates for one-time fill
        Dancer shift: excuses member ONLY
        '''
        self.excused = True
        self.save()
        if 'Dancer' not in self.job.name:
            return self.duplicate()
        
    def get_recurrence_display(self):
        if self.recur_rule:
            if self.recur_rule.interval == 1:
                if self.recur_rule.frequency == 'd':
                    return 'day'
                if self.recur_rule.frequency == 'w':
                    return 'week'
                if self.recur_rule.frequency == 'm':
                    return 'month'
            if self.recur_rule.frequency == 'd':
                return '%s days' % self.recur_rule.interval
            if self.recur_rule.frequency == 'w':
                return '%s weeks' % self.recur_rule.interval
            if self.recur_rule.frequency == 'm':
                return '%s months' % self.recur_rule.interval


def turnout(start, end=None):
    ''' #189: break down shifts based on yes/excused/unexcused, etc. '''
    if end is None:
        end = start + datetime.timedelta(1)
    days = [calc_turnout(date) for date in m_models.daterange(start, end)]
    # I hereby apologize to whoever has to read the following line of code
    totals = dict( [ (desc, sum([ x[desc] for x in days])) 
             for desc in days[0].keys() if desc != 'date' ] )
    return {'days':days, 'totals':totals}

def calc_turnout(date):
    tasks = Task.objects.filter(time__range=(date, date+datetime.timedelta(1)))
    # exclude 9:00am tasks, which are usually non-shift meeting attendance, etc.
    tasks = tasks.exclude(time=datetime.datetime.combine(date, datetime.time(9)))
    return {'date': date,
            'slots': tasks.filter(excused=False).count(),
            'yes': tasks.filter(excused=False, member__isnull=False, hours_worked__gt=0).count(),
            'unexcused': tasks.filter(excused=False, member__isnull=False, hours_worked=0).count(),
            'unfilled': tasks.filter(excused=False, member__isnull=True).count(),
            'excused': tasks.filter(excused=True, member__isnull=False).count(),
            'makeup': tasks.filter(makeup=True).count(),
            'banked': tasks.filter(banked=True).count()}

# unused below

class Timecard(models.Model):
    """
    Keep track of the time worked on a task (through assignment)
    """
    task = models.ForeignKey(Task)
    start = models.DateTimeField()
    end = models.DateTimeField()
    
    def __unicode__(self):
        work = self.end - self.start
        return u"%s hrs of %s" % (work.seconds / 3600, self.task.job)

#class RecurringShift(models.Model):
#    """
#    A recurring shift is members typical workshift made up of a series of tasks
#    """  
#    job = models.ForeignKey(Job)
#    member = models.ForeignKey(Member, null=True)
#    frequency_days = models.IntegerField()
#    start = models.DateTimeField(null=True, blank=True)
#    hours = models.IntegerField()
#
#    def __unicode__(self):
#        return u"%s hrs of %s every %s weeks" % (self.hours, self.job.name, self.frequency)

#class RecurringTaskManager(TaskManager):
#    'Manager with only recurring tasks'
#    def get_query_set(self):
#        return super(RecurringTaskManager, self).get_query_set().exclude(frequency='')
#
#class SingleTaskManager(TaskManager):
#    'Manager with only singleton tasks'
#    def get_query_set(self):
#        return super(SingleTaskManager, self).get_query_set().filter(frequency='')

    #recurring = RecurringTaskManager()
    #singles = SingleTaskManager()

#class Substitute(models.Model):
#    """
#    A substitute worker for a task.
#    """
#    sub_for = models.ForeignKey(Task, related_name='subs')
#    member = models.ForeignKey(Member, null=True, blank=True)
#    account = models.ForeignKey(Account, null=True, blank=True)
    

    #def get_occur_times(self, after, before):
    #    frequency = getattr(rrule, self.get_frequency_display().upper())
    #    recur = rrule.rrule(frequency, dtstart=self.time, 
    #            interval=self.interval)
    #    recur_set = rrule.rruleset()
    #    recur_set.rrule(recur)
    #    for excluded in self.excluded_times.all():
    #        recur_set.exdate(excluded.time)
    #    occur_times = recur_set.between(after, before)
    #    return occur_times

