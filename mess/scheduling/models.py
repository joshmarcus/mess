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

class Task(models.Model):
    """
    A task is an instance of a job
    """
    job = models.ForeignKey(Job)
    deadline = models.DateTimeField()
    start = models.DateTimeField(null=True, blank=True)
    hours = models.IntegerField()
    
    class Meta:
        ordering = ['-deadline', 'start']
    
    def is_assigned(self):
        if self.assignment:
            return True
        else:
            return False
    
    def __unicode__(self):
        return u"%s hrs of %s before %s" % (self.hours, self.job.name, self.deadline.date())

class Assignment(models.Model):
    """
    Associate a member with a task event
    """
    member = models.ForeignKey(Member)
    task = models.OneToOneField(Task)
    
    class Meta:
        ordering = ['task']
    
    def __unicode__(self):
        return u"%s: %s" % (self.member, self.task)

class Timecard(models.Model):
    """
    Keep track of the time worked on a task (through assignment)
    """
    assignment = models.ForeignKey(Assignment)
    start = models.DateTimeField()
    end = models.DateTimeField()
    
    def __unicode__(self):
        work = self.end - self.start
        return u"%s hrs of %s" % (work.seconds / 3600, self.assignment.task.job)
