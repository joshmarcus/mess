import datetime

from django.db import models
from mess.membership.models import Member


class Skill(models.Model):
    """
    Skills needed to perform jobs
    """
    name = models.CharField(max_length=100, unique=True)
    
    def __unicode__(self):
        return self.name

JOB_CHOICES = (
    ('s','Staff'),
    ('p','Paid'),
    ('m','Member'),
)
class Job(models.Model):
    """
    Job description / title
    """
    name = models.CharField(max_length=100, unique=True)
    desc = models.TextField(blank=True)
    type = models.CharField(max_length=1, choices=JOB_CHOICES, blank=True)
    freeze_days = models.IntegerField(default=7)
    hours_multiplier = models.IntegerField(default=1)
    skill_required = models.ForeignKey(Skill, null=True)

    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class RecurringShift(models.Model):
    """
    A recurring shift is members typical workshift made up of a series of tasks
    """  
    job = models.ForeignKey(Job)
    member = models.ForeignKey(Member, null=True)
    frequency_days = models.IntegerField()
    start = models.DateTimeField(null=True, blank=True)
    hours = models.IntegerField()

    def __unicode__(self):
        return u"%s hrs of %s every %s weeks" % (self.hours, self.job.name, self.frequency)


class Task(models.Model):
    """
    A task is an instance of a job that occurs once
    """
    job = models.ForeignKey(Job)
    deadline = models.DateTimeField()
    start = models.DateTimeField(null=True, blank=True)
    member = models.ForeignKey(Member, null=True)
    recurrence = models.ForeignKey(RecurringShift, null=True, blank=True)
    hours = models.IntegerField()
    member = models.ForeignKey(Member, null=True, blank=True)
    
    class Meta:
        ordering = ['-deadline', 'start']
    
    def is_assigned(self):
        if self.member:
            return True
        else:
            return False
    
    def __unicode__(self):
        return u"%s hrs of %s before %s" % (self.hours, self.job.name, self.deadline.date())

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
