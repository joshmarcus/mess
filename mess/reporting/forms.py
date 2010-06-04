import datetime

from django import forms
from mess.autocomplete import AutoCompleteWidget
from mess.accounting import models as a_models
from mess.membership import models as m_models

LIST_OBJECT_CHOICES = (
    ('Accounts', 'Accounts'),
    ('Members', 'Members'),
    ('Tasks', 'Tasks'),
    ('Logs', 'Logs'),
)
LIST_INCLUDE_CHOICES = (
    ('Active', 'Active'),
    ('All', 'All (Active + Inactive)'),
    ('Present', 'Present Only (no LOA)'),
)

class ListFilterForm(forms.Form):
    # this really is required, but not if the form wasn't submitted...
    object = forms.ChoiceField(required=False, choices=LIST_OBJECT_CHOICES)
    include = forms.ChoiceField(required=False, choices=LIST_INCLUDE_CHOICES)
    filter = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows':4, 'wrap':'off'}))
    order_by = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows':2, 'wrap':'off'}))
    output = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows':6, 'wrap':'off'}))

class TransactionFilterForm(forms.Form):
    start = forms.DateTimeField(initial=datetime.date.today())
    end = forms.DateTimeField(initial=datetime.date.today()+datetime.timedelta(1))
    list_each = forms.BooleanField(required=False)
    type = forms.ChoiceField(required=False, choices=
           (('','All'),) + a_models.PURCHASE_CHOICES + a_models.PAYMENT_CHOICES)
    note = forms.CharField(required=False)

class DateRangeForm(forms.Form):
    start = forms.DateField()
    end = forms.DateField()

class HoursBalanceChangesFilterForm(forms.Form):
    start = forms.DateField(required=False) 
    end = forms.DateField(required=False) 
    account = forms.ModelChoiceField(m_models.Account.objects.all(),
        widget=AutoCompleteWidget('account_spiffy',
            view_name='membership-autocomplete', canroundtrip=True),
        required=False)

    def full_clean(self):
        ''' set defaults for start and end '''
        self.data = self.data.copy()      # make QueryDict mutable
        today = datetime.date.today()
        if 'start' not in self.data:
            if 'account' in self.data:
                self.data['start'] = datetime.date(1900,1,1)
            else:
                self.data['start'] = today - datetime.timedelta(7)
        if 'end' not in self.data:
            self.data['end'] = today + datetime.timedelta(1)
        super(HoursBalanceChangesFilterForm,self).full_clean()
