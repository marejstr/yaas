from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.models import User


class RegisterUserForm(forms.Form):

    username = forms.CharField(required=False,
                               max_length=100,
                               label='username')

    password = forms.CharField(required=False,
                               max_length=20,
                               label='password',
                               widget=forms.PasswordInput)

    email = forms.EmailField(required=False, label='email')


class EditAccountForm(forms.Form):

    email = forms.EmailField(required=False, label='New email')

    password = forms.CharField(required=False,
                               max_length=20,
                               label='New password',
                               widget=forms.PasswordInput)
