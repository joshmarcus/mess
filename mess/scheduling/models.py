import datetime
from dateutil import rrule

from django.db import models
from mess.membership.models import Account, Member

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
            related_name='required by')
    skills_trained = models.ManyToManyField(Skill, blank=True, 
            related_name='trained by')

    def __unicode__(self):
        return self.name
    
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
        return self.all().filter(models.Q(member=None) | models.Q(account=None))

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
        return str(self.job) + ' - ' + str(self.time)

    @property
    def assigned(self):
        return bool(self.member and self.account)

    @property
    def unexcused(self):
        return (self.hours_worked == 0 and not self.excused)

    @property
    def timecard_submitted(self):
        return (self.hours_worked is not None)

    def get_end(self):
        delta_hours = datetime.timedelta(hours=float(self.hours))
        end = self.time + delta_hours
        return end

    def get_next_shift(self):
        if self.recur_rule:
            future_tasks = self.recur_rule.task_set.filter(time__gt=self.time)
            next_task = future_tasks.order_by('time')[0]
            return next_task.time
        else:
            return None

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


# unused below

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

