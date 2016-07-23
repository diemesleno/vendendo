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


class OccupationArea(models.Model):
    name = models.CharField(max_length=100)
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('crm:occupationarea-index')


class Customer(models.Model):
    name = models.CharField(max_length=100)
    legal_personality_choices = ((u'N', u'Pessoa Física'),
                                 (u'L', u'Pessoa Jurídica'))
    legal_personality = models.CharField(max_length=1,
                                         choices=legal_personality_choices)
    category_choices = ((u'U', u'Não Qualificado'),
                        (u'Q', u'Qualificado'),
                        (u'P', u'Prospecção'))
    category = models.CharField(max_length=1,
                                choices=category_choices)
    contact1_name = models.CharField(max_length=200)
    contact1_email = models.EmailField(max_length=254)
    contact1_tel = models.CharField(max_length=20)
    contact1_position = models.CharField(max_length=100)
    contact2_name = models.CharField(max_length=200)
    contact2_email = models.EmailField(max_length=254)
    contact2_tel = models.CharField(max_length=20)
    contact2_position = models.CharField(max_length=100)
    contact3_name = models.CharField(max_length=200)
    contact3_email = models.EmailField(max_length=254)
    contact3_tel = models.CharField(max_length=20)
    contact3_position = models.CharField(max_length=100)
    notes = models.TextField(null=True, blank=True)
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE)
    occupationarea = models.ForeignKey('OccupationArea')
    responsible_seller = models.ForeignKey('auth.User')

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('crm:customer-index')


class SaleStage(models.Model):
    name = models.CharField(max_length=100)
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('crm:salestage-index')


class CustomerService(models.Model):
    definition_types = ((u'P', u'Produto'),
                        (u'S', u'Serviço'))
    status_choices = ((u'A', u'Active'),
                      (u'I', u'Inactive'))

    name = models.CharField(max_length=200, null=False)
    definition = models.CharField(max_length=1,
                                  choices=definition_types,
                                  null=False)
    description = models.TextField()
    notes = models.TextField()
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE)
    status = models.CharField(max_length=1,
                              choices=status_choices,
                              default='A',
                              null=False)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('crm:customerservice-index')
