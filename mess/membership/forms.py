from django import newforms as forms

from membership.models import Member

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
