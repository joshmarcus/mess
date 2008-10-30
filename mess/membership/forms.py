from django import forms
from django.contrib.auth.models import User
from django.forms import formsets
from django.forms.models import modelformset_factory

from mess.membership.models import Member, Account, Address, Phone, Email

class PhoneForm(forms.ModelForm):
    class Meta:
        model = Phone
        exclude = ('member',)

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = ('member',)

class EmailForm(forms.ModelForm):
    class Meta:
        model = Email
        exclude = ('member',)

AddressFormSet = modelformset_factory(Address, can_delete=True, extra=0,
        exclude=('member',))
        #min_num=1)
PhoneFormSet = modelformset_factory(Phone, can_delete=True, extra=0,
        exclude = ('member',))
        #min_num=1)
EmailFormSet = modelformset_factory(Email, can_delete=True, extra=0,
        exclude = ('member',))
        #min_num=1)

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ('status', 'work_status', 'has_key', 'primary_account')
    # TODO: add validator for primary_account in accounts

class RelatedAccountsForm(forms.Form):
    def __init__(self, member_instance, *args, **kwargs):
        super(RelatedAccountsForm, self).__init__(*args, **kwargs)
        # TODO: make this a dropdown multiple choice
        if member_instance:
            initial = [obj.pk for obj in member_instance.accounts.all()]
        else:
            initial = None
        self.fields['accounts'] = forms.ModelMultipleChoiceField(
            queryset=Account.objects.all(), initial=initial, required=False,
            help_text='<p class="helptext">Hold down "Control", or "Command" on a Mac, to select more than one.</p>')

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name')
        # TODO: better error checking on username -- no spaces!

class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        exclude = ('balance',)

SORT_CHOICES = (
        ('alpha', 'Alphabetical'),
        ('newjoin', 'Date Joined (newest first)'),
        ('oldjoin', 'Date Joined (oldest first)'),
)

class MemberListFilterForm(forms.Form):
    search = forms.CharField(required=False)
    sort_by = forms.ChoiceField(choices=SORT_CHOICES)
    active = forms.BooleanField(initial=True, required=False)
    inactive = forms.BooleanField(initial=True, required=False)
    quit = forms.BooleanField(initial=True, required=False)
    missing = forms.BooleanField(initial=True, required=False)
    leave_of_absence = forms.BooleanField(initial=True, required=False)
