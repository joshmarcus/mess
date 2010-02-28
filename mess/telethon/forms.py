import datetime

from django import forms
from mess.autocomplete import AutoCompleteWidget
from mess.telethon import models
from mess.membership import models as m_models

CRITERIA_CHOICES = (
    ('active', 'all active members'),
    ('pledges', 'pledges'),
    ('loans', 'loans')
)

class SearchForm(forms.Form):
    member = forms.ModelChoiceField(m_models.Member.objects.all(),
        widget=AutoCompleteWidget('member_spiffy',
            view_name='membership-autocomplete', canroundtrip=True),
        required=False, help_text='* = include inactive')
    criteria = forms.ChoiceField(choices=CRITERIA_CHOICES)


