# coding:utf-8
from django.db import models
from django.contrib import auth
from crm.models import Organization, UserOrganization


class UserComplement(models.Model):
    user_account = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    organization_active = models.ForeignKey('crm.Organization', on_delete=models.CASCADE)

    def __unicode__(self):
        return str(self.organization_active)
