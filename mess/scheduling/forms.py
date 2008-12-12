from django import forms
from django.forms.models import formset_factory

from mess.scheduling import models

AFFECT_CHOICES = (
    (0, 'this time'),
    (1, 'all times'),
)

class TaskForm(forms.ModelForm):
    class Meta:
        model = models.Task
    time = forms.DateTimeField(widget=forms.SplitDateTimeWidget())
    affect = forms.ChoiceField(choices=AFFECT_CHOICES)

class JobForm(forms.ModelForm):
    class Meta:
        model = models.Job

class SkillForm(forms.ModelForm):
    class Meta:
        model = models.Skill

class TimecardForm(forms.ModelForm):
    class Meta:
        model = models.Timecard

class WorkerForm(forms.ModelForm):
    class Meta:
        model = models.Task
        fields = ('id', 'member', 'account')
    
WorkerAddFormSet = formset_factory(WorkerForm, extra=1) #, min_num=1)
WorkerFormSet = formset_factory(WorkerForm, extra=0) #, min_num=1)

