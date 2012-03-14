from django.forms import ModelForm
from django.contrib.admin import widgets
from mess.events.models import Orientation, Location

class OrientationForm(ModelForm):
    class Meta:
        model = Orientation

    def  __init__(self, *args, **kwargs):
        super(OrientationForm, self).__init__(*args, **kwargs)
        self.fields["description"].required=False

class LocationForm(ModelForm):
    class Meta:
        model = Location

    def  __init__(self, *args, **kwargs):
        super(LocationForm, self).__init__(*args, **kwargs)
