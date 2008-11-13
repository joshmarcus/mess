import datetime

from django.db import models
from mess.membership.models import Account, Member

JOB_TYPES = (
    ('s','Staff'),
    ('p','Paid'),
    ('m','Member'),
)
RECURRENCE_UNITS = (
    ('d', 'days'),
    ('w', 'weeks'),
    ('m', 'months'),
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
    deadline = models.DateTimeField(null=True, blank=True)
    start = models.DateTimeField(null=True, blank=True)
    account = models.ForeignKey(Account, null=True, blank=True)
    member = models.ForeignKey(Member, null=True, blank=True)
    hours = models.DecimalField(max_digits=4, decimal_places=2)
    recurrence_freq = models.IntegerField(default=0)
    recurrence_unit = models.CharField(max_length=1, choices=RECURRENCE_UNITS, 
            default='w')
    
    class Meta:
        ordering = ['-deadline', 'start']
    
    def __unicode__(self):
        return u"%s hrs of %s before %s" % (self.hours, self.job.name, 
                self.deadline.date())


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

