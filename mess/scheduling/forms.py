from django import forms

from mess.scheduling import models

class TaskForm(forms.ModelForm):
    class Meta:
        model = models.Task

class JobForm(forms.ModelForm):
    class Meta:
        model = models.Job

class SkillForm(forms.ModelForm):
    class Meta:
        model = models.Skill

class TimecardForm(forms.ModelForm):
    class Meta:
        model = models.Timecard

class TaskGroupForm(forms.ModelForm):
    class Meta:
        model = models.Task
        exclude = ('member', 'account')

class WorkerForm(forms.ModelForm):
    class Meta:
        model = models.Task
        fields = ('member', 'account')
    
