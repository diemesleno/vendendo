# coding:utf-8
from django.shortcuts import render
from django.views.generic import base, ListView, CreateView, UpdateView, \
    DeleteView, TemplateView, FormView
from django.template.response import TemplateResponse
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from crm.models import Organization, UserOrganization, OccupationArea, Customer
from crm.forms import OrganizationForm, SellerFindForm, SellerForm, \
    OccupationAreaForm, CustomerForm
from userapp.models import UserComplement
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from django.conf import settings
from django.core.mail import send_mail
import uuid
import hashlib


class Sendx(object):

    @staticmethod
    def send_invite(self, user_organization):
        try:
            subject = "Você foi convidado! Vendendo CRM"
            body = "Olá "+str(user_organization.user_account.first_name)+", <br /><br />Você foi convidado por <b>"+str(self.request.user.first_name)+"</b> para ser um de seus vendedores na <b>"+str(user_organization.organization.name)+"</b>. <br /><br /> Clique no link a seguir para aceitar o convite: <br /><a href='"+str(settings.INVITE_HOST)+"/invite/activate/?code="+str(user_organization.code_activating)+"'>"+str(settings.INVITE_HOST)+"/invite/activate/?code="+str(user_organization.code_activating)+"</a>"
            print "subject: " + str(subject)
            print "body: " + str(body)
            print "to: " + str(user_organization.user_account.email)
            send_mail(subject, body, "hostmaster@vendendo.com.br",
                                     [user_organization.user_account.email],
                                     html_message=body)
            return True
        except Exception, e:
            return "Erro interno: " + str(e.message)


class SessionMixin(object):

    def get_context_data(self, **kwargs):
        context = super(SessionMixin, self).get_context_data(**kwargs)
        user_account = User.objects.get(id=self.request.user.id)
        organizations = UserOrganization.objects.filter(
                            user_account=user_account,
                            status_active='A')
        organization_active = UserComplement.objects.get(
                                user_account=user_account).organization_active
        type_user_organization = UserOrganization.objects.get(
                                    user_account=user_account,
                                    organization=organization_active).type_user
        context['type_user_organization'] = type_user_organization
        context['organization_active'] = organization_active
        context['organizations'] = organizations
        return context


class SuccessPage(TemplateView):
    template_name = 'crm/success-template.html'


class ErrorPage(TemplateView):
    template_name = 'crm/error-template.html'


class Dashboard(LoginRequiredMixin, SessionMixin, TemplateView):
    template_name = 'crm/dashboard.html'


# Organization Views
class OrganizationSecMixin(object):

    def dispatch(self, *args, **kwargs):
        u = self.request.user
        o = Organization.objects.get(pk=self.kwargs['pk'])

        if not UserOrganization.objects.filter(user_account=u,
                                               organization=o,
                                               type_user='A').exists():
            return redirect('crm:error-index')
        return super(OrganizationSecMixin, self).dispatch(*args, **kwargs)


class OrganizationIndex(LoginRequiredMixin, SessionMixin, ListView):
    template_name = 'crm/organization_index.html'
    context_object_name = 'my_organizations'

    def get_queryset(self):
        user_account = User.objects.get(id=self.request.user.id).id
        return UserOrganization.objects.filter(user_account=user_account,
                                               type_user='A',
                                               status_active='A')


class OrganizationCreate(LoginRequiredMixin, SessionMixin, CreateView):
    model = Organization
    form_class = OrganizationForm

    def form_valid(self, form):
        organization = form.save()
        user_organization = UserOrganization()
        user_organization.user_account = self.request.user
        user_organization.organization = organization
        user_organization.type_user = 'A'
        user_organization.status_active = 'A'
        user_organization.save()
        return super(OrganizationCreate, self).form_valid(form)


class OrganizationUpdate(LoginRequiredMixin, SessionMixin,
                         OrganizationSecMixin, UpdateView):
    model = Organization
    form_class = OrganizationForm


class OrganizationDelete(LoginRequiredMixin, SessionMixin,
                         OrganizationSecMixin, DeleteView):
    model = Organization
    success_url = reverse_lazy('crm:organization-index')


# Seller Views
class SellerSecMixin(object):

    def dispatch(self, *args, **kwargs):
        user = self.request.user
        organization = UserOrganization.objects.get(
                                pk=self.kwargs['pk']).organization

        if not UserOrganization.objects.filter(user_account=user,
                                               organization=organization,
                                               type_user='A').exists():
            return redirect('crm:seller-index')
        return super(SellerSecMixin, self).dispatch(*args, **kwargs)


class SellerUserSecMixin(object):

    def dispatch(self, *args, **kwargs):
        user = self.request.user
        organization_active = UserComplement.objects.get(
                                  user_account=user).organization_active
        seller_user = User.objects.get(pk=self.kwargs['pk'])
        is_seller_here = UserOrganization.objects.filter(
                             user_account=seller_user,
                             organization=organization_active,
                             type_user='S').exists()
        is_admin_logon = UserOrganization.objects.filter(
                             user_account=user,
                             organization=organization_active,
                             type_user='A').exists()

        if is_seller_here and is_admin_logon:
            return super(SellerUserSecMixin, self).dispatch(*args, **kwargs)
        return redirect('crm:seller-index')


class SellerIndex(LoginRequiredMixin, SessionMixin, ListView):
    template_name = 'crm/seller_index.html'
    context_object_name = 'sellers'

    def get_queryset(self):
        user_account = User.objects.get(id=self.request.user.id).id
        organization_active = UserComplement.objects.get(
                                user_account=user_account).organization_active
        return UserOrganization.objects.filter(
            organization=organization_active, type_user='S')


class SellerFind(LoginRequiredMixin, SessionMixin, FormView):
    template_name = 'crm/seller_find_form.html'
    form_class = SellerFindForm

    def get_form_kwargs(self):
        kwargs = super(SellerFind, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        self.request.session['email_find'] = form.cleaned_data['email']
        # Verify if new e-mail
        if User.objects.filter(email=form.cleaned_data['email']).exists():
            self.success_url = reverse_lazy('crm:seller-join')
        else:
            # Create Seller
            self.success_url = reverse_lazy('crm:seller-add')
        return super(SellerFind, self).form_valid(form)


class SellerCreate(LoginRequiredMixin, SessionMixin, CreateView):
    model = UserOrganization
    template_name = 'crm/seller_form.html'
    success_url = reverse_lazy('crm:seller-index')
    form_class = SellerForm

    def get_context_data(self, **kwargs):
        context = super(SellerCreate, self).get_context_data(**kwargs)
        context['email_find'] = self.request.session['email_find']
        return context

    def form_valid(self, form):
        user = form.save(commit=False)
        user.email = self.request.session['email_find']
        user.username = hashlib.md5(user.email).hexdigest()[-30:]
        salt = uuid.uuid4().hex
        new_pass = str(hashlib.md5(salt.encode() +
                                   user.email.encode()).hexdigest())[-8:]
        user.set_password(new_pass)
        user.save()
        user_account = User.objects.get(id=self.request.user.id).id
        organization_active = UserComplement.objects.get(
                                user_account=user_account).organization_active
        user_complement = UserComplement()
        user_complement.user_account = user
        user_complement.organization_active = organization_active
        user_complement.save()

        user_organization = UserOrganization()
        user_organization.user_account = user
        user_organization.organization = organization_active
        user_organization.type_user = 'S'
        code_activating = hashlib.md5(user.email +
                                      str(organization_active.id)
                                      ).hexdigest()[-30:]
        user_organization.code_activating = code_activating
        user_organization.save()
        try:
            Sendx.send_invite(self, user_organization)
        except Exception, e:
            form.add_error(None, str(e.message))
        return super(SellerCreate, self).form_valid(form)


class SellerJoin(LoginRequiredMixin, SessionMixin, CreateView):
    model = UserOrganization
    template_name = 'crm/seller_join_form.html'
    success_url = reverse_lazy('crm:seller-index')
    fields = []

    def get_context_data(self, **kwargs):
        context = super(SellerJoin, self).get_context_data(**kwargs)
        user_join = User.objects.get(email=self.request.session['email_find'])
        context['email_find'] = user_join.email
        context['full_name'] = str(user_join.first_name) + str(
                                user_join.last_name)
        return context

    def form_valid(self, form):
        user_organization = form.save(commit=False)

        user_account = User.objects.get(
                           email=self.request.session['email_find'])
        admin_account = User.objects.get(id=self.request.user.id)
        organization_active = UserComplement.objects.get(
                                user_account=admin_account).organization_active

        user_organization.user_account = user_account
        user_organization.organization = organization_active
        user_organization.type_user = 'S'
        code_activating = hashlib.md5(self.request.session['email_find'] +
                                      str(organization_active.id)
                                      ).hexdigest()[-30:]
        user_organization.code_activating = code_activating
        user_organization.save()
        Sendx.send_invite(self, user_organization)
        return super(SellerJoin, self).form_valid(form)


class SellerDeactivate(LoginRequiredMixin, SessionMixin,
                       SellerSecMixin, UpdateView):
    model = UserOrganization

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.status_active = 'I'
        self.object.save()
        return redirect('crm:seller-index')


class SellerActivate(LoginRequiredMixin, SessionMixin,
                     SellerSecMixin, UpdateView):
    model = UserOrganization

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.status_active = 'A'
        self.object.save()
        return redirect('crm:seller-index')


class SellerDelete(LoginRequiredMixin, SessionMixin,
                   SellerSecMixin, DeleteView):
    model = UserOrganization
    success_url = reverse_lazy('crm:seller-index')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        user_account = self.object.user_account
        self.object.delete()

        if not UserOrganization.objects.filter(
                user_account=user_account).exists():
            user_account.delete()
        return HttpResponseRedirect(success_url)


class SellerInviteActivate(base.View):

    def get(self, request):
        code = request.GET.get("code", False)
        if code:
            if UserOrganization.objects.filter(code_activating=code,
                                               status_active='N').exists():
                user_organization = UserOrganization.objects.get(
                                        code_activating=code)
                user_organization.status_active = 'A'
                user_organization.save()
                return redirect('crm:success-index')
        return redirect('crm:error-index')


class SellerInvite(LoginRequiredMixin, SessionMixin,
                   SellerSecMixin, UpdateView):
    model = UserOrganization

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        Sendx.send_invite(self, self.object)
        return redirect('crm:seller-index')


# Occupation Area Views
class OccupationAreaIndex(LoginRequiredMixin, SessionMixin, ListView):
    template_name = 'crm/occupationarea_index.html'
    context_object_name = 'my_occupationareas'

    def get_queryset(self):
        user_account = User.objects.get(id=self.request.user.id)
        organization_active = UserComplement.objects.get(
                                user_account=user_account).organization_active
        return OccupationArea.objects.filter(organization=organization_active)


class OccupationAreaCreate(LoginRequiredMixin, SessionMixin, CreateView):
    model = OccupationArea
    form_class = OccupationAreaForm

    def form_valid(self, form):
        occupation_area = form.save(commit=False)
        user_account = User.objects.get(id=self.request.user.id).id
        organization_active = UserComplement.objects.get(
                                 user_account=user_account).organization_active
        occupation_area.organization = organization_active
        occupation_area.save()
        return super(OccupationAreaCreate, self).form_valid(form)


class OccupationAreaUpdate(LoginRequiredMixin, SessionMixin, UpdateView):
    model = OccupationArea
    form_class = OccupationAreaForm


class OccupationAreaDelete(LoginRequiredMixin, SessionMixin, DeleteView):
    model = OccupationArea
    success_url = reverse_lazy('crm:occupationarea-index')


# Customer Area Views
class CustomerIndex(LoginRequiredMixin, SessionMixin, ListView):
    template_name = 'crm/customer_index.html'
    context_object_name = 'my_customers'

    def get_queryset(self):
        user_account = User.objects.get(id=self.request.user.id)
        organization_active = UserComplement.objects.get(
                                user_account=user_account).organization_active
        return Customer.objects.filter(organization=organization_active)


class CustomerCreate(LoginRequiredMixin, SessionMixin, CreateView):
    model = Customer
    form_class = CustomerForm

    def form_valid(self, form):
        customer = form.save(commit=False)
        user_account = User.objects.get(id=self.request.user.id)
        organization_active = UserComplement.objects.get(
                                 user_account=user_account).organization_active
        customer.organization = organization_active
        customer.responsible_seller = user_account
        customer.save()
        user_complement = UserComplement.objects.get(
                                 user_account=user_account,
                                 organization_active=organization_active)
        user_complement.customers.add(customer)
        user_complement.save()
        return super(CustomerCreate, self).form_valid(form)


class CustomerUpdate(LoginRequiredMixin, SessionMixin, UpdateView):
    model = Customer
    form_class = CustomerForm


class CustomerDelete(LoginRequiredMixin, SessionMixin, DeleteView):
    model = Customer
    success_url = reverse_lazy('crm:customer-index')
