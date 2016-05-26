from django.shortcuts import render
from django.views.generic import base, ListView, TemplateView
from django.template.response import TemplateResponse
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from crm.models import UserOrganization
from userapp.models import UserComplement


class SessionMixin(object):

    def get_context_data(self, **kwargs):
        context = super(SessionMixin, self).get_context_data(**kwargs)
        user_account = User.objects.get(id=self.request.user.id).id
        organizations = UserOrganization.objects.filter(user_account=user_account)
        organization_active = UserComplement.objects.get(user_account=user_account).organization_active
        type_user_organization = UserOrganization.objects.get(
                                     user_account=user_account, 
                                     organization=organization_active).type_user
        context['type_user_organization'] = type_user_organization
        context['organization_active'] = organization_active
        context['organizations'] = organizations
        return context


class Dashboard(LoginRequiredMixin, SessionMixin, TemplateView):
    template_name = 'crm/dashboard.html'


class OrganizationIndex(LoginRequiredMixin, SessionMixin, ListView):
    template_name = 'crm/organization_index.html'
    context_object_name = 'my_organizations'

    def get_queryset(self):
        user_account = User.objects.get(id=self.request.user.id).id
        return UserOrganization.objects.filter(user_account=user_account,
                                               type_user='A',
                                               status_active=True)
