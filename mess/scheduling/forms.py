from dateutil import parser
from datetime import datetime

from django import forms
from django.forms.models import inlineformset_factory

from mess.scheduling import models

AFFECT_CHOICES = (
    (0, 'this time'),
    (1, 'all times'),
)

class ParseDateTimeField(forms.Field):
    """ 
    DateTime field that accepts natural-language input.
    """
    def clean(self, value):
        super(ParseDateTimeField, self).clean(value)
        if value in (None, ''):
            return None
        if value[1] in (None, ''):
            raise forms.ValidationError(u'Enter a valid time.')
        if isinstance(value, datetime):
            return value
        if isinstance(value, list):
            # Input comes from a SplitDateTimeWidget, for example. So, it's two
            # components: date and time.
            if len(value) != 2:
                raise forms.ValidationError(self.error_messages['invalid'])
            value = '%s %s' % tuple(value)
        try:
            return parser.parse(value)
        except ValueError:
            raise forms.ValidationError(u'Enter a valid time.')

class TaskForm(forms.ModelForm):
    class Meta:
        model = models.Task
    time = ParseDateTimeField(widget=forms.SplitDateTimeWidget())
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

class RecurForm(forms.ModelForm):
    class Meta:
        model = models.RecurRule
        exclude = ('start', )

class WorkerForm(forms.ModelForm):
    class Meta:
        model = models.Worker
        fields = ('member', 'account')
    #taskid = forms.IntegerField(required=False, widget=forms.HiddenInput())
    
AddWorkerFormSet = inlineformset_factory(models.Task, models.Worker, extra=1)
WorkerFormSet = inlineformset_factory(models.Task, models.Worker, extra=0) #, min_num=1)

