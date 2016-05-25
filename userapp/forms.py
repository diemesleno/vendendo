# coding:utf-8
from django import forms
from django.contrib.auth.models import User


class NewUserForm(forms.ModelForm):
    error_messages = {
        'required': 'Campo Obrigatório.',
        'invalid': 'Campo Inválido'
    }
    first_name = forms.CharField(required=True, error_messages=error_messages)
    email = forms.CharField(required=True, error_messages={
        'required': 'Campo Obrigatório.',
        'invalid': 'Entre com um usuário válido. Este campo pode conter somente \
            letras, números e os caracteres @ . + - _.'
    })
    username = forms.CharField(required=False)
    password = forms.CharField(required=True, error_messages=error_messages)
    organization = forms.CharField(required=True, error_messages=error_messages)

    class Meta:
        model = User
        fields = ('username',
                  'email',
                  'first_name',
                  'last_name',
                  'password')


class EditUserForm(forms.ModelForm):
    error_messages = {
        'required': 'Campo Obrigatório.',
        'invalid': 'Campo Inválido'
    }
    first_name = forms.CharField(required=True, error_messages=error_messages)
    email = forms.CharField(required=True, error_messages={
        'required': 'Campo Obrigatório.',
        'invalid': 'Entre com um usuário válido. Este campo pode conter somente \
            letras, números e os caracteres @ . + - _.'
    })
    username = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ('username',
                  'email',
                  'first_name',
                  'last_name')


class LoginForm(forms.ModelForm):
    error_messages = {
        'required': 'Campo Obrigatório.',
        'invalid': 'Campo Inválido'
    }
    username = forms.CharField(required=True, error_messages={
        'required': 'Campo Obrigatório.',
        'invalid': 'Entre com um usuário válido. Este campo pode conter somente \
            letras, números e os caracteres @ . + - _.'
    })
    password = forms.CharField(required=True, error_messages=error_messages)

    class Meta:
        model = User
        fields = ('username',
                  'password')
