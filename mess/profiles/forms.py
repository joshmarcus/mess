from django import forms
from django.forms.models import modelformset_factory
from mess.profiles.models import UserProfile, Address, Phone, Email

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile

class PhoneForm(forms.ModelForm):
    class Meta:
        model = Phone

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address

class EmailForm(forms.ModelForm):
    class Meta:
        model = Email

AddressFormSet = modelformset_factory(Address, can_delete=True, extra=0)
PhoneFormSet = modelformset_factory(Phone, can_delete=True, extra=0)
EmailFormSet = modelformset_factory(Email, can_delete=True, extra=0)

form_map = {
    'userprofile': UserProfileForm,
    'phone': PhoneForm,
    'address': AddressForm,
    'email': EmailForm,
}
