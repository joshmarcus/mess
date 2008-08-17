from django import forms
from mess.profiles.models import UserProfile, Address, Phone, Email

class PhoneForm(forms.ModelForm):
	class Meta:
		model = Phone
