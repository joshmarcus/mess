from django import forms
from django.contrib.auth.models import User, Group
from django.forms import formsets
from django.forms.models import inlineformset_factory, modelformset_factory
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from mess.membership import models
from mess.events import models as e_models
from mess.autocomplete import AutoCompleteWidget
import datetime

AddressFormSet = inlineformset_factory(models.Member, models.Address, 
        extra=0) #, min_num=1)
EmailFormSet = inlineformset_factory(models.Member, models.Email, 
        extra=0) #, min_num=1)
PhoneFormSet = inlineformset_factory(models.Member, models.Phone, 
        extra=0) #, min_num=1)
LeaveOfAbsenceFormSet = inlineformset_factory(models.Member, models.LeaveOfAbsence, 
        extra=0) #, min_num=1)
RelatedAccountFormSet = inlineformset_factory(models.Member, 
        models.AccountMember, exclude=('primary_account',), extra=0)
RelatedMemberFormSet = inlineformset_factory(models.Account, 
        models.AccountMember, exclude=('primary_account',), extra=0)

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

class LeaveOfAbsenceForm(forms.ModelForm):
    class Meta:
        model = models.LeaveOfAbsence
        exclude = ('member',)

class RelatedAccountForm(forms.ModelForm):
    class Meta:
        model = models.AccountMember
        exclude = ('member', 'primary_account')

class RelatedMemberForm(forms.ModelForm):
    class Meta:
        model = models.AccountMember
        exclude = ('account', 'primary_account')

class MemberForm(forms.ModelForm):
    class Meta:
        model = models.Member
        exclude = ('status', 'user', 'equity_held')

class UserEmailForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email',)

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'groups')
    # username pulled straight from django/contrib/auth/forms.py
    username = forms.RegexField(label=_("Username"), max_length=30, 
            regex=r'^\w+$', help_text = _("Required. 30 characters or fewer. Alphanumeric characters only (letters, digits and underscores)."),
            error_message = _("This value must contain only letters, numbers and underscores."))
    # groups pulled from django/contrib/auth/models.py and augmented
    groups = forms.ModelMultipleChoiceField(Group.objects.all(),
        help_text=_('Hold down "Control", or "Command" on a Mac, to select more than one.'),
        required=False)

class AccountForm(forms.ModelForm):
    class Meta:
        model = models.Account
        exclude = ('balance', 'deposit', 'members', 'can_shop')

MEMBER_SORT_CHOICES = (
    ('alpha', 'Alphabetical'),
    ('newjoin', 'Date joined (newest first)'),
    ('oldjoin', 'Date joined (oldest first)'),
)

ACCOUNT_SORT_CHOICES = (
    ('alpha', 'Alphabetical'),
    ('recent', 'Most recently added'),
    ('hours', 'Hours balance (high to low)'),
    ('balance', 'Account balance (high to low)'),
)

class MemberListFilterForm(forms.Form):
    search = forms.CharField(required=False)
    sort_by = forms.ChoiceField(choices=MEMBER_SORT_CHOICES)
    active = forms.BooleanField(initial=True, required=False)
    leave_of_absence = forms.BooleanField(initial=False, required=False)
    missing = forms.BooleanField(initial=False, required=False)
    missing_delinquent = forms.BooleanField(initial=False, required=False)
    departed = forms.BooleanField(initial=False, required=False)

class DateForm(forms.Form):
    day = forms.DateField(initial = datetime.date.today)

class PickMemberForm(forms.Form):
    member = forms.ModelChoiceField(models.Member.objects.all(),
        widget=AutoCompleteWidget('member_spiffy',
            view_name='membership-autocomplete', canroundtrip=True))

class TemporaryBalanceLimitForm(forms.ModelForm):
    class Meta:
        model = models.TemporaryBalanceLimit
        fields = ['limit','until']

class LoaForm(forms.Form):
    ENDDEF = 365  # days from today for endtime default
    start = forms.DateField(initial=datetime.date.today)
    default_end = datetime.date.today() + datetime.timedelta(ENDDEF)
    end = forms.DateField(initial=default_end)
    c_tuple = (('short', 'free each shift for one-time fill'),
               ('long', 'remove members from shifts entirely'))
    shifts_during_LOA = forms.ChoiceField(choices=c_tuple,
                                          widget=forms.RadioSelect, 
                                          initial='long')

class AccountListFilterForm(forms.Form):
    search = forms.CharField(required=False)
    sort_by = forms.ChoiceField(choices=ACCOUNT_SORT_CHOICES)
    active = forms.BooleanField(initial=True, required=False)
    inactive = forms.BooleanField(initial=False, required=False)
#   can_shop = forms.BooleanField(initial=True, required=False)
#   ebt_only = forms.BooleanField(initial=True, required=False)

def mess_get_orientation_choices(upcoming_orientations_only):
    """ 
    Helper function that returns all upcoming (and active)
    orientations as well as our two special orientations:
    Returning member, and None of these dates work for me 
    """
    if not upcoming_orientations_only:
        returning_member_orientation = e_models.Orientation.objects.get(id=1)

    orientations = e_models.Orientation.objects.filter(active=True).filter(start__gte=datetime.datetime.now())

    if not upcoming_orientations_only:
        no_dates_orientation = e_models.Orientation.objects.get(id=2)
    
    orientation_choices = [('','')]

    if not upcoming_orientations_only:
        orientation_choices.append((returning_member_orientation.id, returning_member_orientation.name))

    for orientation in orientations:
        orientation_choices.append((orientation.id, orientation.name))

    if not upcoming_orientations_only:
        orientation_choices.append((no_dates_orientation.id, no_dates_orientation.name))

    return orientation_choices


class MemberSignUpForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(MemberSignUpForm, self).__init__(*args, **kwargs)
        self.fields["orientation"].choices = mess_get_orientation_choices(False)

#    def clean_email(self):
#        data = self.cleaned_data["email"]
#
#        if User.objects.filter(email=data).count() > 0:
#            raise ValidationError(u'The email address %s is already in use by an existing member. If you are a returning member, please write to membership@mariposa.coop to inquire about restoring your membership at Mariposa.')
#
#        return data

    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(required=True)
    street_address = forms.CharField(required=True)
    city = forms.CharField(required=True, initial="Philadelphia")
    state = forms.CharField(required=True, initial="PA")
    postal_code = forms.CharField(required=True, initial="19143")
    referral_source = forms.ChoiceField(required=False, choices=models.REFERRAL_SOURCES)
    referring_member = forms.CharField(required=False)
    terms = forms.BooleanField(required=True, initial=False)
    orientation = forms.ChoiceField(required=True)
    equity_paid = forms.ChoiceField(required=True, choices=models.EQUITY_PAID_OPTIONS)

class MemberSignUpEditForm(forms.ModelForm):
    class Meta:
        model = models.MemberSignUp

class MemberSignUpReviewForm(forms.Form):

#    def __init__(self, *args, **kwargs):
#        super(MemberSignUpReviewForm, self).__init__(*args, **kwargs)
#        
#        members = models.Member.objects.filter(date_departed__isnull=True)
#        member_choices = [('','')]
#
#        for member in members:
#            member_choices.append((member.id, str(member)))
#        
#        self.fields["referring_member"].choices = member_choices

    def clean_user_name(self):
     
        value = self.cleaned_data['user_name']

        if (value.strip()==''):
            raise ValidationError(u'The user name must not be blank')
    
        if (User.objects.filter(username=value.strip()).count() > 0):
            raise ValidationError(u'The user name %s already exists' % value)

        return value

    record_id = forms.IntegerField(widget=forms.HiddenInput, required=False)
    selected = forms.BooleanField(initial=False, required=False)
    name = forms.CharField(widget=forms.HiddenInput, required=False)
    user_name = forms.CharField(max_length=30, required=False)
    email = forms.CharField(widget=forms.HiddenInput, required=False)
    phone = forms.CharField(widget=forms.HiddenInput, required=False)
    address1 = forms.CharField(widget=forms.HiddenInput, required=False)
    city = forms.CharField(widget=forms.HiddenInput, required=False)
    state = forms.CharField(widget=forms.HiddenInput, required=False)
    postal_code = forms.CharField(widget=forms.HiddenInput, required=False)
    referral_source = forms.CharField(widget=forms.HiddenInput, required=False)
    referring_member = forms.ChoiceField(required=False)
    orientation = forms.CharField(widget=forms.HiddenInput, required=False)
    equity_paid = forms.CharField(widget=forms.HiddenInput, required=False)
    payment_verified = forms.BooleanField(initial=False, required=False)

class OrientationSignUpForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        super(OrientationSignUpForm, self).__init__(*args, **kwargs)
        self.fields["orientation"].choices = mess_get_orientation_choices(True)

    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(required=True)
    orientation = forms.ChoiceField(required=True)

AccountMemberFlagsFormSet = modelformset_factory(models.AccountMember, 
                    exclude=('account', 'member', 'primary_account'), 
                    extra=0)

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

