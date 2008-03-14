from django import newforms as forms

from mess.membership.models import Member

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
