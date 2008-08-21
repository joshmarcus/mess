from django import forms

from mess.membership.models import Member, Account
from mess.profiles.models import UserProfile, Address, Phone, Email
from django.contrib.auth.models import User

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
class UserForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ('first_name', 'last_name', 'is_active')
		# could include is_staff and is_superuser, but security risk
class UserProfileForm(forms.ModelForm):
	class Meta:
		model = UserProfile

class AccountForm(forms.ModelForm):
	class Meta:
		model = Account
