# coding:utf-8
from django.db import models
from django.contrib import auth
from django.core.urlresolvers import reverse
from datetime import date, datetime
from django.utils import timezone
from django.db.models import Q, F, Sum


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
    type_user_choices = ((u'A', u'Administrador'),
                         (u'M', u'Gerente'),
                         (u'S', u'Comercial'))
    type_status_choices = ((u'A', u'Ativo'),
                           (u'I', u'Inativo'),
                           (u'N', u'Convidado'))
    type_user = models.CharField(max_length=1, choices=type_user_choices)
    status_active = models.CharField(max_length=1,
                                     choices=type_status_choices,
                                     default='N')
    code_activating = models.CharField(max_length=200, null=True)

    def __unicode__(self):
        return str(self.user_account.first_name) + ' ' + str(self.user_account.last_name)

    def get_absolute_url(self):
        return reverse('crm:member-index')


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
                        (u'Q', u'Cliente Potencial'),
                        (u'P', u'Cliente da Base'))
    category = models.CharField(max_length=1,
                                choices=category_choices)
    relevance_choices = ((0, u'0%'),
                         (10, u'10%'),
                         (20, u'20%'),
                         (30, u'30%'),
                         (40, u'40%'),
                         (50, u'50%'),
                         (60, u'60%'),
                         (70, u'70%'),
                         (80, u'80%'),
                         (90, u'90%'),
                         (100, u'100%'))
    relevance = models.IntegerField(default=0,
                                    choices=relevance_choices)
    notes = models.TextField(null=True, blank=True)
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE)
    occupationarea = models.ForeignKey('OccupationArea')
    responsible_seller = models.ForeignKey('auth.User', null=True, blank=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('crm:customer-index')

    def get_opportunities_won(self):
        return Opportunity.objects.filter(customer=self, stage__final_stage=True)

    @property
    def opportunities_won_value(self):
        result = 0
        for opportunity in self.get_opportunities_won():
            result += opportunity.expected_value
        return result


class SaleStage(models.Model):
    conclusion_choices = ((u'W', u'Ganha'),
                          (u'L', u'Perdida'))
    name = models.CharField(max_length=100)
    order_number = models.IntegerField(default=0)
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE)
    final_stage = models.BooleanField(default=False)
    conclusion = models.CharField(max_length=1, choices=conclusion_choices, null=True, blank=True)
    add_customer = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('crm:salestage-index')

    @property
    def get_opportunity_value(self):
        result = 0
        opportunities = Opportunity.objects.filter(stage=self)
        for opportunity in opportunities:
            result += opportunity.expected_value
        return result

    def get_opportunity_value_by_type_user(self, is_admin, user_account):
        result = 0
        if is_admin:
            opportunities = Opportunity.objects.filter(stage=self)
        else:
            opportunities = Opportunity.objects.filter(stage=self, seller=user_account)
        for opportunity in opportunities:
            result += opportunity.expected_value
        return result


class CustomerService(models.Model):
    definition_types = ((u'P', u'Produto'),
                        (u'S', u'Serviço'))
    status_choices = ((u'A', u'Ativo'),
                      (u'I', u'Inativo'))

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


class Opportunity(models.Model):
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    seller = models.ForeignKey('auth.User')
    stage = models.ForeignKey('SaleStage', on_delete=models.CASCADE)
    expected_month = models.CharField(max_length=7)
    created = models.DateTimeField(auto_now_add=True)
    description_opportunity = models.CharField(max_length=100)

    @property
    def expected_value(self):
        value = OpportunityItem.objects.filter(opportunity=self).aggregate(num=Sum(F('expected_amount')*F('expected_value'),output_field=models.DecimalField(decimal_places=2)))['num']
        if not value:
            value = 0
        return value

    def __unicode__(self):
        return  self.customer.name + ' - ' +  self.description_opportunity

    def get_absolute_url(self):
        return reverse('crm:opportunity-index')


class OpportunityItem(models.Model):
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE)
    opportunity = models.ForeignKey('Opportunity', on_delete=models.CASCADE)
    customer_service = models.ForeignKey('CustomerService', on_delete=models.CASCADE)
    description = models.TextField(null=True)
    expected_value = models.DecimalField(max_digits=19, decimal_places=2, null=True)
    expected_amount = models.DecimalField(max_digits=19, decimal_places=2, null=True)

    def __unicode__(self):
        return self.id + ':' + self.organization.name + ' | ' + self.opportunity.id + ' [' + self.customer_service.name + ']'


class Activity(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    opportunity = models.ForeignKey('Opportunity', on_delete=models.CASCADE)
    type_activity_choices = ((u'T', u'Telefonema'),
                             (u'E', u'E-mail'),
                             (u'V', u'Visita'),
                             (u'O', u'Outras Tarefas'))
    type_activity = models.CharField(max_length=1,
                                     choices=type_activity_choices)
    details = models.TextField(null=True, blank=True)
    deadline = models.DateTimeField(null=False)
    created = models.DateTimeField(auto_now_add=True)
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE)
    responsible_seller = models.ForeignKey('auth.User')
    completed = models.BooleanField(default=False)
    completed_date = models.DateField(null=True, blank=True)

    @property
    def is_late(self):
        return timezone.now() > self.deadline

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('crm:activity-index')


class Contact(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    contact_name = models.CharField(max_length=200)
    contact_email = models.EmailField(max_length=254)
    contact_tel = models.CharField(max_length=20)
    contact_position = models.CharField(max_length=100)

    def __unicode__(self):
        return self.contact_name
