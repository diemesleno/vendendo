# coding:utf-8
from django.db import models
from django.contrib import auth
from crm.models import Organization, UserOrganization, Customer


class UserComplement(models.Model):
    user_account = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    organization_active = models.ForeignKey('crm.Organization', on_delete=models.CASCADE, null=True)
    customers = models.ManyToManyField('crm.Customer')

    def __unicode__(self):
        return str(self.user_account.first_name)
