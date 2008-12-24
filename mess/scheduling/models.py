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

class TaskManager(models.Manager):
    'Custom manager to add extra methods'
    def unassigned(self):
        return self.all().filter(models.Q(member=None) | models.Q(account=None))

#class RecurringTaskManager(TaskManager):
#    'Manager with only recurring tasks'
#    def get_query_set(self):
#        return super(RecurringTaskManager, self).get_query_set().exclude(frequency='')
#
#class SingleTaskManager(TaskManager):
#    'Manager with only singleton tasks'
#    def get_query_set(self):
#        return super(SingleTaskManager, self).get_query_set().filter(frequency='')


class RecurRule(models.Model):
    start = models.DateTimeField()
    frequency = models.CharField(max_length=1, choices=FREQUENCIES, blank=True)
    interval = models.PositiveIntegerField(default=1)
    until = models.DateTimeField(null=True, blank=True)

    def save(self, force_insert=False, force_update=False):
        # TODO: for newly created RecurRule, create tasks for two years
        # for modified, remove old tasks and create new ones
        super(RecurRule, self).save(force_insert, force_update)

    def update_buffer(self):
        # update the 2-year date buffer
        pass

class Task(models.Model):
    """
    A task is a scheduled occurrence of a job.  The time is a start time 
    unless deadline is checked for the related job.
    """
    job = models.ForeignKey(Job)
    time = models.DateTimeField()
    hours = models.DecimalField(max_digits=4, decimal_places=2)
    member = models.ForeignKey(Member, null=True, blank=True)
    account = models.ForeignKey(Account, null=True, blank=True)
    hours_worked = models.DecimalField(max_digits=4, decimal_places=2, 
            null=True, blank=True)
    excused = models.BooleanField()
    makeup = models.BooleanField()
    recur_rule = models.ForeignKey(RecurRule, null=True, blank=True)

    objects = TaskManager()
    #recurring = RecurringTaskManager()
    #singles = SingleTaskManager()
    
    class Meta:
        ordering = ['job']

    def __unicode__(self):
        return unicode(self.job) + ' - ' + str(self.time)

    def get_end(self):
        delta_hours = datetime.timedelta(hours=float(self.hours))
        end = self.time + delta_hours
        return end

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
    #
    #def get_recurrence_display(self):
    #    if self.frequency and self.interval:
    #        if self.interval == 1:
    #            if self.frequency == 'd':
    #                return 'day'
    #            if self.frequency == 'w':
    #                return 'week'
    #            if self.frequency == 'm':
    #                return 'month'
    #        if self.frequency == 'd':
    #            return '%s days' % self.interval
    #        if self.frequency == 'w':
    #            return '%s weeks' % self.interval
    #        if self.frequency == 'm':
    #            return '%s months' % self.interval


class Exclusion(models.Model):
    recur_rule = models.ForeignKey(RecurRule)
    date = models.DateTimeField()


class Substitute(models.Model):
    """
    A substitute worker for a task on a specific day.
    """
    sub_for = models.ForeignKey(Task, related_name='subs')
    time = models.DateTimeField()
    member = models.ForeignKey(Member, null=True, blank=True)
    account = models.ForeignKey(Account, null=True, blank=True)
    

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

