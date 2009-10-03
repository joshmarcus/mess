from django import forms
from mess.forum import models

class AddPostForm(forms.ModelForm):
    class Meta:
        model = models.Post
        exclude = ('timestamp','deleted')

    forum = forms.ModelChoiceField(models.Forum.objects.all(),
            widget=forms.HiddenInput())
    author = forms.CharField(required=False, widget=forms.HiddenInput())
    subject = forms.CharField(widget=forms.TextInput(attrs={'size':50}))
    body = forms.CharField(widget=forms.Textarea(attrs={'cols':80}))
    
    # hide subject if it's already in the initial data
    def __init__(self, *args, **kwargs):
        super(AddPostForm, self).__init__(*args, **kwargs)
        if self.initial.get('subject') or self.data.get('subject'):
            self.fields['subject'].widget = forms.HiddenInput()

    def save(self, author):
        self.cleaned_data['author'] = author
        super(AddPostForm, self).save()
