from django import forms
from mess.forum import models

class AddPostForm(forms.Form):
    forum = forms.ModelChoiceField(models.Forum.objects.all(),
            widget=forms.HiddenInput())
    subject = forms.CharField(widget=forms.TextInput(attrs={'size':50}))
    body = forms.CharField(widget=forms.Textarea(attrs={'cols':80}))
    
    # hide subject if it's already in the initial data
    def __init__(self, *args, **kwargs):
        super(AddPostForm, self).__init__(*args, **kwargs)
        if self.initial.get('subject') or self.data.get('subject'):
            self.fields['subject'].widget = forms.HiddenInput()

    def save(self, author):
        self.instance = models.Post.objects.create(
                        forum=self.cleaned_data.get('forum'),
                        author=author,
                        subject=self.cleaned_data.get('subject'),
                        body=self.cleaned_data.get('body'))
