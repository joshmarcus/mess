from django import newforms as forms

from mess.membership.models import Member
from mess.membership.models import Account

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member

class AccountForm(forms.ModelForm):
	class Meta:
		model = Account
