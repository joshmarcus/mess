from django import newforms as forms

from mess.contact.models import Address

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address

