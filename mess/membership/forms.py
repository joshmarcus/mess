from django import forms
from django.contrib.auth.models import User
from django.forms import formsets
from django.forms.models import inlineformset_factory, modelformset_factory
from django.utils.translation import ugettext_lazy as _

from mess.membership import models

AddressFormSet = inlineformset_factory(models.Member, models.Address, 
        extra=0) #, min_num=1)
EmailFormSet = inlineformset_factory(models.Member, models.Email, 
        extra=0) #, min_num=1)
PhoneFormSet = inlineformset_factory(models.Member, models.Phone, 
        extra=0) #, min_num=1)
RelatedAccountFormSet = inlineformset_factory(models.Member, 
        models.AccountMember, extra=0)
RelatedMemberFormSet = inlineformset_factory(models.Account, 
        models.AccountMember, extra=0)

# forms below needed for dynamic formsets
class AddressForm(forms.ModelForm):
    class Meta:
        model = models.Address
        exclude = ('member',)

class EmailForm(forms.ModelForm):
    class Meta:
        model = models.Email
        exclude = ('member',)

class PhoneForm(forms.ModelForm):
    class Meta:
        model = models.Phone
        exclude = ('member',)

class RelatedAccountForm(forms.ModelForm):
    class Meta:
        model = models.AccountMember
        exclude = ('member',)

class RelatedMemberForm(forms.ModelForm):
    class Meta:
        model = models.AccountMember
        exclude = ('account',)

class MemberForm(forms.ModelForm):
    class Meta:
        model = models.Member

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name')
    # username pulled straight from django/contrib/auth/forms.py
    username = forms.RegexField(label=_("Username"), max_length=30, 
            regex=r'^\w+$', help_text = _("Required. 30 characters or fewer. Alphanumeric characters only (letters, digits and underscores)."),
            error_message = _("This value must contain only letters, numbers and underscores."))

class AccountForm(forms.ModelForm):
    class Meta:
        model = models.Account
        exclude = ('balance', 'members')

SORT_CHOICES = (
        ('alpha', 'Alphabetical'),
        ('newjoin', 'Date Joined (newest first)'),
        ('oldjoin', 'Date Joined (oldest first)'),
)

class MemberListFilterForm(forms.Form):
    search = forms.CharField(required=False)
    sort_by = forms.ChoiceField(choices=SORT_CHOICES)
    active = forms.BooleanField(initial=True, required=False)
    leave_of_absence = forms.BooleanField(initial=False, required=False)
    missing = forms.BooleanField(initial=False, required=False)
    missing_delinquent = forms.BooleanField(initial=False, required=False)
    departed = forms.BooleanField(initial=False, required=False)

class AccountListFilterForm(forms.Form):
    search = forms.CharField(required=False)
    note_q = forms.CharField(required=False)

#class RelatedAccountsForm(forms.Form):
#    def __init__(self, member_instance, *args, **kwargs):
#        super(RelatedAccountsForm, self).__init__(*args, **kwargs)
#        # TODO: make this a dropdown multiple choice
#        if member_instance:
#            initial = [obj.pk for obj in member_instance.accounts.all()]
#        else:
#            initial = None
#        self.fields['accounts'] = forms.ModelMultipleChoiceField(
#            queryset=Account.objects.all(), initial=initial, required=False,
#            help_text='<p class="helptext">Hold down "Control", or "Command" on a Mac, to select more than one.</p>')

