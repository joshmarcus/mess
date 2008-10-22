from django import forms
from django.contrib.auth.models import User
from django.forms import formsets

from mess.membership.models import Member, Account

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ('status', 'work_status', 'has_key', 'primary_account')
    # TODO: add validator for primary_account in accounts

class RelatedAccountsForm(forms.Form):
    def __init__(self, member_instance, *args, **kwargs):
        super(RelatedAccountsForm, self).__init__(*args, **kwargs)
        # TODO: make this a dropdown multiple choice
        self.fields['accounts'] = forms.ModelMultipleChoiceField(
            queryset=Account.objects.all(), 
            initial=[obj.pk for obj in member_instance.accounts.all()],
            help_text='<p class="helptext">Hold down "Control", or "Command" on a Mac, to select more than one.</p>')

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        # only change is_staff and is_superuser in the admin
        fields = ('first_name', 'last_name')

class AccountForm(forms.ModelForm):
    class Meta:
        model = Account

SORT_CHOICES = (
        ('alpha', 'Alphabetical'),
        ('newjoin', 'Date Joined (newest first)'),
        ('oldjoin', 'Date Joined (oldest first)'),
)

class MemberListFilterForm(forms.Form):
    search = forms.CharField()
    sort_by = forms.ChoiceField(choices=SORT_CHOICES)
    active = forms.BooleanField(initial=True, required=False)
    inactive = forms.BooleanField(initial=True, required=False)
    quit = forms.BooleanField(initial=True, required=False)
    missing = forms.BooleanField(initial=True, required=False)
    leave_of_absence = forms.BooleanField(initial=True, required=False)
