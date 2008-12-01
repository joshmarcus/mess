import datetime

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
    freeze_days = models.IntegerField(default=7)
    hours_multiplier = models.IntegerField(default=1)
    skill_required = models.ForeignKey(Skill, blank=True, null=True, 
            related_name='required by')
    skill_trained = models.ForeignKey(Skill, blank=True, null=True, 
            related_name='trained by')

    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Task(models.Model):
    """
    A task is a scheduled occurrence of a job (or occurences, if recurring), 
    and has either a deadline or a start time.
    """
    job = models.ForeignKey(Job)
    time = models.DateTimeField()
    hours = models.DecimalField(max_digits=4, decimal_places=2)
    deadline = models.BooleanField()
    member = models.ForeignKey(Member, null=True, blank=True)
    account = models.ForeignKey(Account, null=True, blank=True)
    frequency = models.CharField(max_length=1, choices=FREQUENCIES, blank=True)
    interval = models.PositiveIntegerField(default=1)
    
    class Meta:
        ordering = ['time']

    def __unicode__(self):
        if self.member:
            value = u"(%s for %s) " % (self.member.user.username, self.account_or_default())
        else:
            value = u"(unassigned) "
        if self.deadline:
            value += u"%s hrs of %s before %s" % (self.hours, self.job.name, self.time.date())
        else:
            value += u"%s: %s hrs of %s" % (self.time, self.hours, self.job.name)
            if self.interval > 0:
                value = value + u" " + u"every %s %s" % (self.interval, self.frequency)
        return value

    def account_or_default(self):
        if not self.account:
            return self.member.primary_account()
        return self.account

    def get_end(self):
        delta_hours = datetime.timedelta(hours=float(self.hours))
        end = self.time + delta_hours
        return end
    

class TaskExcludeTime(models.Model):
    task = models.ForeignKey(Task, related_name='excluded_times')
    time = models.DateTimeField()

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

