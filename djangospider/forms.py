from django import forms

class UsernameForm(forms.Form):
    username = forms.CharField(label='username', max_length=25, widget=forms.TextInput(attrs={'placeholder': 'enter vlr username [case sensitive]'}))