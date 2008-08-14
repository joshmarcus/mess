import datetime

from django.db import models
from mess.membership.models import Member

JOB_CHOICES = (
    ('p','Paid'),
    ('m','Member'),
)

class Job(models.Model):
    """
    Job description / title
    """
    name = models.CharField(max_length=40, unique=True)
    desc = models.TextField(blank=True)
    type = models.CharField(max_length=1, choices=JOB_CHOICES, blank=True)

    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

FREQUENCY_CHOICES = (
    ('4','Every 4 Weeks'),
    ('6','Every 6 Weeks'),
)

class RecurringShift(models.Model):
    """
    A recurring shift is members typical workshift made up of a series of tasks
    """   
    job = models.ForeignKey(Job)
    member = models.ForeignKey(Member, null=True)
    frequency = models.CharField(max_length=1, choices=FREQUENCY_CHOICES)
    start = models.DateTimeField(null=True, blank=True)
    hours = models.IntegerField()

    def __unicode__(self):
        return unicode(self.name)


class Task(models.Model):
    """
    A task is an instance of a job that occurs once
    """
    job = models.ForeignKey(Job)
    deadline = models.DateTimeField()
    start = models.DateTimeField(null=True, blank=True)
    member = models.ForeignKey(Member, null=True)
    recurrence = models.ForeignKey(RecurringShift, null=True)
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
