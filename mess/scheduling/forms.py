from dateutil import parser
from datetime import datetime

from django import forms
from django.forms.models import inlineformset_factory, modelformset_factory
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

class AccountTangleWidget(AutoCompleteWidget):
    ''' 
    We want to click a member, and auto-fill their account field.
    But then the accountid will be a string.
    (I don't want to make a special xhr just to get the numeric accountid.)
    This widget gets the numeric accountid after submission.
    '''
    def __init__(self):
        super(AccountTangleWidget, self).__init__('account', 
                view_name='membership-autocomplete', canroundtrip=True)

    def value_from_datadict(self, data, files, name):
        raw_data = data.get(name, None)
        if raw_data is None or raw_data == '':
            return raw_data
        try:
            return int(raw_data)
        except ValueError:
            # media/js/autocomplete.js protects numeric account name with 'Z'
            # assert raw_data[0] == 'Z'
            return m_models.Account.objects.get(name=raw_data[1:]).id

class TaskForm(forms.ModelForm):
    class Meta:
        model = models.Task
        exclude = ['recur_rule', 'hours_worked']
    time = ParseDateTimeField(widget=forms.SplitDateTimeWidget())
    account = forms.ModelChoiceField(m_models.Account.objects.all(),
        widget=AccountTangleWidget(), required=False) 
    member = forms.ModelChoiceField(m_models.Member.objects.all(),
        widget=AutoCompleteWidget('member_spiffy', 
            view_name='membership-autocomplete', canroundtrip=True), 
        required=False, help_text='* = include inactive') 
    #recur_rule = forms.IntegerField(initial=self.instance.recur_rule.id, 
    #        widget=forms.HiddenInput)
    #affect = forms.ChoiceField(choices=AFFECT_CHOICES)

    # must set both account and member.  if only one is set, clear it.
    def clean(self):
        if not self.cleaned_data.get('account') or not self.cleaned_data.get('member'):
            self.cleaned_data['account'] = self.cleaned_data['member'] = None
        return self.cleaned_data

class JobForm(forms.ModelForm):
    skills_required = forms.ModelMultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            queryset=models.Skill.objects.all(),
            required=False)
    skills_trained = forms.ModelMultipleChoiceField(
            widget=forms.CheckboxSelectMultiple,
            queryset=models.Skill.objects.all(),
            required=False)

    class Meta:
        model = models.Job

class SkillForm(forms.ModelForm):
    class Meta:
        model = models.Skill

class TimecardForm(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput)
    hours_worked = forms.DecimalField(required=False, 
                    widget=forms.TextInput(attrs={'size':'2'}))
    shift_status = forms.ChoiceField(choices=(
        ('unexcused', 'Unexcused'),
        ('worked', 'Worked'),
        ('excused', 'Excused'),
        )
    )
    makeup = forms.BooleanField(required=False)
    banked = forms.BooleanField(required=False)
    

class RecurForm(forms.ModelForm):
    class Meta:
        model = models.RecurRule

TimecardFormSet = modelformset_factory(models.Task, extra=0, 
    fields=('hours_worked', 'excused', 'makeup', 'banked'))

class PickTaskForm(forms.Form):
    ''' 
    warning: don't render this form without setting the queryset
    use form.fields['task'].queryset = models.Task.objects.filter(...)
    '''
    task = forms.ModelChoiceField(models.Task.objects.all(), 
           empty_label=None, widget=forms.RadioSelect())

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

