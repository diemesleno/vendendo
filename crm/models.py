# coding:utf-8
from django.db import models
from django.contrib import auth


class Organization(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField('auth.User', through='UserOrganization')

    def __unicode__(self):
        return self.name


class UserOrganization(models.Model):
    user_account = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE)
    type_user_choices = ((u'A', u'Admin'),
                         (u'M', u'Manager'),
                         (u'S', u'Seller'))
    type_user = models.CharField(max_length=1, choices=type_user_choices)
    status_active = models.BooleanField(default=True)

    def __unicode__(self):
        return str(self.id)
