from __future__ import unicode_literals

from django.db import models

class Organization(models.Model):
    user = models.ForeignKey('auth.User')
    name = models.CharField(max_length=100)
