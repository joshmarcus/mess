from django import newforms as forms

from mess.people.models import Person

class Search(forms.Form):
    search = forms.CharField(max_length=20)


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
