from dateutil import parser
from datetime import datetime

from django import forms
from django.forms.models import inlineformset_factory
from mess.autocomplete import AutoCompleteWidget

from mess.scheduling import models
from mess.membership import models as m_models

AFFECT_CHOICES = (
    (0, 'all future times'),
    (1, 'this time only'),
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
    account = forms.ModelChoiceField(m_models.Account.objects.all(),
        widget=AutoCompleteWidget('account', 
            view_name='membership-autocomplete', canroundtrip=True), 
        required=False) 
    member = forms.ModelChoiceField(m_models.Member.objects.all(),
        widget=AutoCompleteWidget('member_with_paccount', 
            view_name='membership-autocomplete', canroundtrip=True), 
        required=False) 
    #recur_rule = forms.IntegerField(initial=self.instance.recur_rule.id, 
    #        widget=forms.HiddenInput)
    #affect = forms.ChoiceField(choices=AFFECT_CHOICES)

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

#class WorkerForm(forms.ModelForm):
#    class Meta:
#        model = models.Worker
#        fields = ('member', 'account')
#    #taskid = forms.IntegerField(required=False, widget=forms.HiddenInput())
#    account = forms.ModelChoiceField(m_models.Account.objects.all(),
#            widget=AutoCompleteWidget('account', 
#                    view_name='membership-autocomplete', canroundtrip=True), 
#            required=False)
#    member = forms.ModelChoiceField(m_models.Member.objects.all(),
#            widget=AutoCompleteWidget('member_with_paccount',
#                    view_name='membership-autocomplete', canroundtrip=True),
#            required=False)
    
#AddWorkerFormSet = inlineformset_factory(models.Task, models.Worker, form=WorkerForm, extra=1)
#WorkerFormSet = inlineformset_factory(models.Task, models.Worker, form=WorkerForm, extra=0) #, min_num=1)

