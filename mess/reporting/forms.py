
from django import forms

LIST_OBJECT_CHOICES = (
    ('Accounts', 'Accounts'),
    ('Members', 'Members'),
)

class ListFilterForm(forms.Form):
    # this really is required, but not if the form wasn't submitted...
    object = forms.ChoiceField(required=False, choices=LIST_OBJECT_CHOICES)
    filter = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows':4}))
    output = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows':6}))

