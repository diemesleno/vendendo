from django.shortcuts import render
from django.views.generic import base, ListView, CreateView, UpdateView, \
    DeleteView, TemplateView
from django.template.response import TemplateResponse
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from crm.models import Organization, UserOrganization
from crm.forms import OrganizationForm
from userapp.models import UserComplement
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect


class SessionMixin(object):

    def get_context_data(self, **kwargs):
        context = super(SessionMixin, self).get_context_data(**kwargs)
        user_account = User.objects.get(id=self.request.user.id).id
        organizations = UserOrganization.objects.filter(
                            user_account=user_account)
        organization_active = UserComplement.objects.get(
                                user_account=user_account).organization_active
        type_user_organization = UserOrganization.objects.get(
                                    user_account=user_account,
                                    organization=organization_active).type_user
        context['type_user_organization'] = type_user_organization
        context['organization_active'] = organization_active
        context['organizations'] = organizations
        return context


class Dashboard(LoginRequiredMixin, SessionMixin, TemplateView):
    template_name = 'crm/dashboard.html'


class OrganizationSecMixin(object):

    def dispatch(self, *args, **kwargs):
        u = self.request.user
        o = Organization.objects.get(pk=self.kwargs['pk'])

        if not UserOrganization.objects.filter(user_account=u,
                                               organization=o,
                                               type_user='A').exists():
            return redirect('crm:organization-index')
        return super(OrganizationSecMixin, self).dispatch(*args, **kwargs)


class OrganizationIndex(LoginRequiredMixin, SessionMixin, ListView):
    template_name = 'crm/organization_index.html'
    context_object_name = 'my_organizations'

    def get_queryset(self):
        user_account = User.objects.get(id=self.request.user.id).id
        return UserOrganization.objects.filter(user_account=user_account,
                                               type_user='A',
                                               status_active=True)


class OrganizationCreate(LoginRequiredMixin, SessionMixin, CreateView):
    model = Organization
    form_class = OrganizationForm

    def form_valid(self, form):
        organization = form.save()
        user_organization = UserOrganization()
        user_organization.user_account = self.request.user
        user_organization.organization = organization
        user_organization.type_user = 'A'
        user_organization.save()
        return super(OrganizationCreate, self).form_valid(form)


class OrganizationUpdate(LoginRequiredMixin, SessionMixin, OrganizationSecMixin, UpdateView):
    model = Organization
    form_class = OrganizationForm


class OrganizationDelete(LoginRequiredMixin, SessionMixin, OrganizationSecMixin, DeleteView):
    model = Organization
    success_url = reverse_lazy('crm:organization-index')


class SellerIndex(LoginRequiredMixin, SessionMixin, ListView):
    template_name = 'crm/seller_index.html'
    context_object_name = 'sellers'

    def get_queryset(self):
        user_account = User.objects.get(id=self.request.user.id).id
