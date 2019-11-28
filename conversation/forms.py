from django import forms
from .models import ChatMessage
from django.contrib.auth.models import User, auth


class ChatForm(forms.Form):
    '''from_user = forms.IntegerField(
        widget=forms.HiddenInput()
    )
    to_user = forms.IntegerField(
        widget=forms.HiddenInput()
    )'''
    source = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )
    text = forms.CharField(
        max_length=128,
        widget=forms.TextInput(
            attrs={'class': 'textbox', 'autocomplete': 'off', 'autofocus': 'on'}),
        help_text='Write here your message!',

    )

    def clean(self):
        cleaned_data = super(ChatForm, self).clean()
        text = cleaned_data.get('text')
        if not text:
            raise forms.ValidationError('You have to write something!')
