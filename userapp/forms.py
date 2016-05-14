# coding:utf-8
from django import forms
from django.contrib.auth.models import User


class NovoUsuarioForm(forms.ModelForm):
    error_messages = {
        'required': 'Campo Obrigatorio.',
        'invalid': 'Campo Invalido'
    }
    first_name = forms.CharField(required=True, error_messages=error_messages)
    email = forms.CharField(required=True, error_messages={
        'required': 'Campo Obrigatorio.',
        'invalid': 'Entre com um username válido. Este campo pode conter somente \
            letras, numeros e os caracteres @ . + - _.'
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


class LoginForm(forms.ModelForm):
    error_messages = {
        'required': 'Campo Obrigatorio.',
        'invalid': 'Campo Invalido'
    }
    username = forms.CharField(required=True, error_messages={
        'required': 'Campo Obrigatorio.',
        'invalid': 'Entre com um username válido. Este campo pode conter somente \
            letras, numeros e os caracteres @ . + - _.'
    })
    password = forms.CharField(required=True, error_messages=error_messages)

    class Meta:
        model = User
        fields = ('username',
                  'password')
