# coding:utf-8
from django.db import models
from django.contrib import auth
from django.core.urlresolvers import reverse


class Organization(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField('auth.User', through='UserOrganization')

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('crm:organization-index')


class UserOrganization(models.Model):
    user_account = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE)
    type_user_choices = ((u'A', u'Admin'),
                         (u'M', u'Manager'),
                         (u'S', u'Seller'))
    type_status_choices = ((u'A', u'Active'),
                           (u'I', u'Inactive'),
                           (u'N', u'Invited'))
    type_user = models.CharField(max_length=1, choices=type_user_choices)
    status_active = models.CharField(max_length=1,
                                     choices=type_status_choices,
                                     default='N')
    code_activating = models.CharField(max_length=200, null=True)

    def __unicode__(self):
        return str(self.id) + ' : ' + str(self.user_account.first_name) + ' (' + str(self.organization.name) + ')'

    def get_absolute_url(self):
        return reverse('crm:seller-index')
