from django import forms
from django.contrib.auth.models import User
from django.forms import formsets

from mess.membership.models import Member, Account

class MemberForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MemberForm, self).__init__(*args, **kwargs)
        self.fields['accounts'] = forms.ModelMultipleChoiceField(queryset=Account.objects.all(), initial=[obj.pk for obj in self.instance.accounts.all()])
    class Meta:
        model = Member
        fields = ('status', 'work_status', 'has_key', 'primary_account')

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        # only change is_staff and is_superuser in the admin
        fields = ('first_name', 'last_name')

class AccountForm(forms.ModelForm):
    class Meta:
        model = Account

