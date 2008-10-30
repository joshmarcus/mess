from django import forms
from django.forms import ModelForm

from mess.scheduling.models import *

class TaskForm(ModelForm):
    class Meta:
        model = Task

class JobForm(ModelForm):
    class Meta:
        model = Job

class SkillForm(ModelForm):
    class Meta:
        model = Skill

class TimecardForm(ModelForm):
    class Meta:
        model = Timecard
