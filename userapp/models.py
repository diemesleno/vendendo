# coding:utf-8
from django.db import models
from django.contrib import auth


class UserComplementar(models.Model):
    usuario = models.ForeignKey('auth.User')
    data_nascimento = models.DateField(blank=True)
    sexo = models.CharField(max_length=1)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    pais = models.CharField(max_length=50)
    avatar = models.CharField(max_length=50, null=True)
    status = models.CharField(max_length=1)
