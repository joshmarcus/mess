from django import forms
from django.forms.models import formset_factory

from mess.scheduling import models

class TaskForm(forms.ModelForm):
    class Meta:
        model = models.Task
    time = forms.DateTimeField(widget=forms.SplitDateTimeWidget())

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
        fields = ('member', 'account')
    
WorkerFormSet = formset_factory(WorkerForm, extra=1) #, min_num=1)

