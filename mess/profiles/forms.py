from django import forms
from mess.profiles.models import UserProfile, Address, Phone, Email

class PhoneForm(forms.ModelForm):
	class Meta:
		model = Phone

class AddressForm(forms.ModelForm):
	class Meta:
		model = Address

class EmailForm(forms.ModelForm):
	class Meta:
		model = Email
