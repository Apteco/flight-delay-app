from django import forms
from django.forms import ModelForm


class LoginUserForm(forms.Form):
    username = forms.CharField(
        label='Username',
        max_length=80,
        required=True
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        max_length=50,
        required=True
    )


class LoginApiForm(forms.Form):
    username = forms.CharField(
        label='Username',
        required=True
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        required=True
    )
    url = forms.CharField(label="System URL")
    system_name = forms.CharField(label="System Name")
    data_view = forms.CharField(label="Data View")

