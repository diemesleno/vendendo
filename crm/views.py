# coding:utf-8
from django.shortcuts import render
from django.views.generic import base, ListView, CreateView, UpdateView, \
    DeleteView, TemplateView, FormView
from django.template.response import TemplateResponse
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from crm.models import Organization, UserOrganization, OccupationArea, \
                       Customer, SaleStage, CustomerService, Opportunity, \
                       OpportunityItem, Activity
from crm.forms import OrganizationForm, SellerFindForm, SellerForm, \
                      OccupationAreaForm, CustomerForm, SaleStageForm,\
                      CustomerServiceForm, OpportunityForm, ActivityForm
from userapp.models import UserComplement
from django.core.urlresolvers import reverse_lazy
from django.utils.functional import cached_property
from django.shortcuts import redirect
from django.conf import settings
from django.core.mail import send_mail
from datetime import datetime
from django.db.models import Q, F, Sum
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

    @cached_property
    def organization_active(self):
        return UserComplement.objects.get(user_account=self.user_account).organization_active

    @cached_property
    def user_account(self):
        return User.objects.get(id=self.request.user.id)

    @cached_property
    def is_admin(self):
        user_account = User.objects.get(id=self.request.user.id)
        if UserOrganization.objects.filter(
                                    user_account=user_account,
                                    organization=self.organization_active).exists():
            type_user_organization = UserOrganization.objects.get(
                                        user_account=user_account,
                                        organization=self.organization_active).type_user
            if type_user_organization == "A":
                return True
            else:
                return False
        return False

    @cached_property
    def organizations(self):
        return UserOrganization.objects.filter(
                            user_account=self.user_account,
                            status_active='A')

    def get_context_data(self, **kwargs):
        context = super(SessionMixin, self).get_context_data(**kwargs)
        user_account = User.objects.get(id=self.request.user.id)
        organizations = UserOrganization.objects.filter(
                            user_account=user_account,
                            status_active='A')
        organization_active = UserComplement.objects.get(
                                user_account=user_account).organization_active
        if organization_active:
            type_user_organization = UserOrganization.objects.get(
                                        user_account=user_account,
                                        organization=organization_active).type_user
        else:
            type_user_organization = None
        # Invite messages
        invites = UserOrganization.objects.filter(Q(user_account=user_account)&Q(type_user='S')&~Q(status_active='A'))

        context['type_user_organization'] = type_user_organization
        context['organization_active'] = organization_active
        context['organizations'] = organizations
        context['invites'] = invites
        return context


class SuccessPage(TemplateView):
    template_name = 'crm/success-template.html'


class ErrorPage(TemplateView):
    template_name = 'crm/error-template.html'


class Dashboard(LoginRequiredMixin, SessionMixin, ListView):
    template_name = 'crm/dashboard.html'
    context_object_name = 'my_activities'

    def get_context_data(self, **kwargs):
        context = super(Dashboard, self).get_context_data(**kwargs)
        context['customers_potential_count'] = Customer.objects.filter(Q(opportunity__isnull=True) | Q(opportunity__stage__final_stage=True), organization=self.organization_active, category='Q').count()
        context['customers_potential_top5'] = Customer.objects.filter(Q(opportunity__isnull=True) | Q(opportunity__stage__final_stage=True), organization=self.organization_active, category='Q').order_by('-relevance')[:5]
        context['opportunities_open_count'] = Opportunity.objects.filter(organization=self.organization_active, stage__final_stage=False).count()
        context['opportunities_open_top5'] = sorted(Opportunity.objects.filter(organization=self.organization_active, stage__final_stage=False)[:5], key=lambda o: o.expected_value, reverse=True)
        context['customers_base_count'] = Customer.objects.filter(organization=self.organization_active, category='P').count()
        context['customers_base_top5'] = Customer.objects.filter(organization=self.organization_active, category='P').order_by('-relevance')[:5]
        context['customers_potential_complete'] = range(context['customers_potential_count'], 5)
        context['opportunities_open_complete'] = range(context['opportunities_open_count'], 5)
        context['customers_base_complete'] = range(context['customers_base_count'], 5)
        # calculate opportunity values by stage
        stages = SaleStage.objects.filter(organization=self.organization_active, final_stage=False).order_by('order_number')
        opportunity_value_stages = "["
        idx = 0
        for stage in stages:
            if stage.get_opportunity_value > 0:
                if idx > 0:
                    opportunity_value_stages += ","
                opportunity_value_stages += "['%s', %s]" % (stage.name, str(stage.get_opportunity_value))
                idx += 1
        opportunity_value_stages += "]"
        context['opportunity_value_stages'] = opportunity_value_stages
        return context

    def get_queryset(self):

        if self.is_admin:
            return Activity.objects.filter(organization=self.organization_active, completed=False).order_by('deadline')[:4]
        else:
            return Activity.objects.filter(organization=self.organization_active, completed=False, responsible_seller=self.user_account).order_by('deadline')[:4]

    def get_template_names(self):
        if self.template_name is None:
            raise ImproperlyConfigured(
                "TemplateResponseMixin requires either a definition of "
                "'template_name' or an implementation of 'get_template_names()'")
        else:
            if not self.organizations:
                self.template_name = 'crm/help_index.html'
            return [self.template_name]


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


class OrganizationActivate(LoginRequiredMixin, SessionMixin, UpdateView):
    model = Organization

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        user_account = User.objects.get(id=self.request.user.id)
        user_complement = UserComplement.objects.get(user_account=user_account)
        user_complement.organization_active = self.object
        user_complement.save()
        return redirect('crm:dashboard-index')


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


# SaleStage Views
class SaleStageIndex(LoginRequiredMixin, SessionMixin, ListView):
    template_name = 'crm/salestage_index.html'
    context_object_name = 'my_salestages'

    def get_queryset(self):
        user_account = User.objects.get(id=self.request.user.id)
        organization_active = UserComplement.objects.get(
                                user_account=user_account).organization_active
        stages = SaleStage.objects.filter(
            organization=organization_active).order_by('order_number')
        return stages


class SaleStageCreate(LoginRequiredMixin, SessionMixin, CreateView):
    model = SaleStage
    form_class = SaleStageForm

    def form_valid(self, form):
        salestage = form.save(commit=False)
        user_account = User.objects.get(id=self.request.user.id).id
        organization_active = UserComplement.objects.get(
                                 user_account=user_account).organization_active
        salestage.organization = organization_active
        salestage.order_number = total_stages = SaleStage.objects.filter(
            organization=organization_active).count()
        salestage.save()
        return super(SaleStageCreate, self).form_valid(form)


class SaleStageUpdate(LoginRequiredMixin, SessionMixin, UpdateView):
    model = SaleStage
    form_class = SaleStageForm


class SaleStageDelete(LoginRequiredMixin, SessionMixin, DeleteView):
    model = SaleStage
    success_url = reverse_lazy('crm:salestage-index')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        organization = self.object.organization
        self.object.delete()
        stages = SaleStage.objects.filter(
                     organization=organization).order_by('order_number')
        for idx,stage in enumerate(stages):
            stage.order_number = idx
            stage.save()
        return redirect('crm:salestage-index')


class SaleStageUp(LoginRequiredMixin, SessionMixin, UpdateView):
    model = SaleStage

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        current_order = self.object.order_number
        organization = self.object.organization
        if current_order > 0:
            previous_stage = SaleStage.objects.get(
                                 organization=organization,
                                 order_number=current_order-1)
            previous_stage.order_number = current_order
            previous_stage.save()
            self.object.order_number = current_order-1
            self.object.save()
        return redirect('crm:salestage-index')


class SaleStageDown(LoginRequiredMixin, SessionMixin, UpdateView):
    model = SaleStage

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        current_order = self.object.order_number
        organization = self.object.organization
        total_stages = SaleStage.objects.filter(
            organization=organization).count()
        if current_order < total_stages-1:
            next_stage = SaleStage.objects.get(
                                 organization=organization,
                                 order_number=current_order+1)
            next_stage.order_number = current_order
            next_stage.save()
            self.object.order_number = current_order+1
            self.object.save()
        return redirect('crm:salestage-index')


# CustomerService Views
class CustomerServiceSecMixin(object):

    def dispatch(self, *args, **kwargs):
        u = self.request.user
        o = CustomerService.objects.get(pk=self.kwargs['pk']).organization

        if not UserOrganization.objects.filter(user_account=u,
                                               organization=o,
                                               type_user='A').exists():
            return redirect('crm:error-index')
        return super(CustomerServiceSecMixin, self).dispatch(*args, **kwargs)


class CustomerServiceIndex(LoginRequiredMixin, SessionMixin, ListView):
    template_name = 'crm/customerservice_index.html'
    context_object_name = 'my_customerservices'

    def get_queryset(self):
        user_account = User.objects.get(id=self.request.user.id)
        organization_active = UserComplement.objects.get(
                                user_account=user_account).organization_active
        return CustomerService.objects.filter(organization=organization_active)


class CustomerServiceCreate(LoginRequiredMixin, SessionMixin, CreateView):
    model = CustomerService
    form_class = CustomerServiceForm

    def form_valid(self, form):
        customerservice = form.save(commit=False)
        user_account = User.objects.get(id=self.request.user.id).id
        organization_active = UserComplement.objects.get(
                                 user_account=user_account).organization_active
        customerservice.organization = organization_active
        customerservice.save()
        return super(CustomerServiceCreate, self).form_valid(form)


class CustomerServiceDelete(LoginRequiredMixin, SessionMixin, CustomerServiceSecMixin, DeleteView):
    model = CustomerService
    success_url = reverse_lazy('crm:customerservice-index')


class CustomerServiceUpdate(LoginRequiredMixin, SessionMixin, CustomerServiceSecMixin, UpdateView):
    model = CustomerService
    form_class = CustomerServiceForm



# Opportunity
class OpportunitySecMixin(object):

    def dispatch(self, *args, **kwargs):
        u = self.request.user
        o = Opportunity.objects.get(pk=self.kwargs['pk']).organization

        if not UserOrganization.objects.filter(user_account=u,
                                               organization=o,
                                               type_user='A').exists():
            return redirect('crm:error-index')
        return super(OpportunitySecMixin, self).dispatch(*args, **kwargs)


class OpportunityIndex(LoginRequiredMixin, SessionMixin, ListView):
    template_name = 'crm/opportunity_index.html'
    context_object_name = 'my_opportunities'

    def get_queryset(self):
        user_account = User.objects.get(id=self.request.user.id)
        organization_active = UserComplement.objects.get(
                                user_account=user_account).organization_active
        return Opportunity.objects.filter(organization=organization_active)


class OpportunityCreate(LoginRequiredMixin, SessionMixin, CreateView):
    model = Opportunity
    form_class = OpportunityForm

    def get_context_data(self, **kwargs):
        context = super(OpportunityCreate, self).get_context_data(**kwargs)
        user_account = User.objects.get(id=self.request.user.id)
        organization_active = UserComplement.objects.get(
                                user_account=user_account).organization_active
        customer_services = CustomerService.objects.filter(
                                organization=organization_active)
        context['customer_services'] = customer_services
        return context

    def form_valid(self, form):
        opportunity = form.save(commit=False)
        user_account = User.objects.get(id=self.request.user.id)
        organization_active = UserComplement.objects.get(
                                 user_account=user_account).organization_active
        opportunity.organization = organization_active
        opportunity.seller = user_account
        opportunity.save()
        products = self.request.POST.getlist('product')
        descriptions = self.request.POST.getlist('description')
        expected_values = self.request.POST.getlist('expected_value_item')
        expected_amounts = self.request.POST.getlist('expected_amount')
        # clear Opportunity Items
        OpportunityItem.objects.filter(opportunity=opportunity).delete()
        # create news opportunity items
        if products:
            for idx,product in enumerate(products):
                opportunity_item = OpportunityItem()
                opportunity_item.opportunity = opportunity
                opportunity_item.organization = opportunity.organization
                customer_service = CustomerService.objects.get(id=product)
                opportunity_item.customer_service = customer_service
                opportunity_item.description = descriptions[idx]
                opportunity_item.expected_value = expected_values[idx]
                opportunity_item.expected_amount = expected_amounts[idx]
                opportunity_item.save()
        #add customer
        if opportunity.stage.add_customer:
            opportunity.customer.category = 'P'
            opportunity.customer.save()
        return super(OpportunityCreate, self).form_valid(form)

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(organization=self.organization_active,
                          **self.get_form_kwargs())


class OpportunityDelete(LoginRequiredMixin, SessionMixin, OpportunitySecMixin, DeleteView):
    model = Opportunity
    success_url = reverse_lazy('crm:opportunity-index')


class OpportunityUpdate(LoginRequiredMixin, SessionMixin, OpportunitySecMixin, UpdateView):
    model = Opportunity
    form_class = OpportunityForm

    def get_context_data(self, **kwargs):
        context = super(OpportunityUpdate, self).get_context_data(**kwargs)
        user_account = User.objects.get(id=self.request.user.id)
        organization_active = UserComplement.objects.get(
                                user_account=user_account).organization_active
        customer_services = CustomerService.objects.filter(
                                organization=organization_active)
        opportunity = Opportunity.objects.get(pk=self.kwargs['pk'])
        opportunity_items = OpportunityItem.objects.filter(
                                organization=organization_active,
                                opportunity=opportunity)
        context['customer_services'] = customer_services
        context['opportunity_items'] = opportunity_items
        return context

    def form_valid(self, form):
        opportunity = form.save()
        products = self.request.POST.getlist('product')
        descriptions = self.request.POST.getlist('description')
        expected_values = self.request.POST.getlist('expected_value_item')
        expected_amounts = self.request.POST.getlist('expected_amount')
        # clear Opportunity Items
        OpportunityItem.objects.filter(opportunity=opportunity).delete()
        # create news opportunity items
        if products:
            for idx,product in enumerate(products):
                opportunity_item = OpportunityItem()
                opportunity_item.opportunity = opportunity
                opportunity_item.organization = opportunity.organization
                customer_service = CustomerService.objects.get(id=product)
                opportunity_item.customer_service = customer_service
                opportunity_item.description = descriptions[idx]
                opportunity_item.expected_value = expected_values[idx]
                opportunity_item.expected_amount = expected_amounts[idx]
                opportunity_item.save()
        #add customer
        if opportunity.stage.add_customer:
            opportunity.customer.category = 'P'
            opportunity.customer.save()
        opportunity.save()
        return super(OpportunityUpdate, self).form_valid(form)

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(organization=self.organization_active,
                          **self.get_form_kwargs())


# Activity Area Views
class ActivityIndex(LoginRequiredMixin, SessionMixin, ListView):
    template_name = 'crm/activity_index.html'
    context_object_name = 'my_activities'

    def get_queryset(self):
        user_account = User.objects.get(id=self.request.user.id)
        organization_active = UserComplement.objects.get(
                                user_account=user_account).organization_active
        if self.is_admin:
            return Activity.objects.filter(organization=organization_active)
        else:
            return Activity.objects.filter(organization=organization_active, responsible_seller=user_account)

class ActivityCreate(LoginRequiredMixin, SessionMixin, CreateView):
    model = Activity
    form_class = ActivityForm

    def form_valid(self, form):
        activity = form.save(commit=False)
        user_account = User.objects.get(id=self.request.user.id)
        organization_active = UserComplement.objects.get(
                                 user_account=user_account).organization_active
        activity.organization = organization_active
        activity.responsible_seller = user_account
        # add completed_date
        if activity.completed:
            if activity.completed_date is None:
                activity.completed_date = datetime.now()
        else:
            activity.completed_date = None
        activity.save()
        return super(ActivityCreate, self).form_valid(form)

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(organization=self.organization_active,
                          **self.get_form_kwargs())


class ActivityUpdate(LoginRequiredMixin, SessionMixin, UpdateView):
    model = Activity
    form_class = ActivityForm

    def form_valid(self, form):
        activity = form.save()
        # add completed_date
        if activity.completed:
            if activity.completed_date is None:
                activity.completed_date = datetime.now()
        else:
            activity.completed_date = None
        activity.save()
        return super(ActivityUpdate, self).form_valid(form)

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(organization=self.organization_active,
                          **self.get_form_kwargs())


class ActivityDelete(LoginRequiredMixin, SessionMixin, DeleteView):
    model = Activity
    success_url = reverse_lazy('crm:activity-index')


# Invite messages Views
class InviteMessageIndex(LoginRequiredMixin, SessionMixin, ListView):
    template_name = 'crm/invite_message_index.html'
    context_object_name = 'my_messages'

    def get_queryset(self):
        user_account = User.objects.get(id=self.request.user.id)
        return UserOrganization.objects.filter(user_account=user_account, type_user='S')


class InviteMessageActivate(LoginRequiredMixin, SessionMixin, UpdateView):
    model = UserOrganization

    def post(self, request, *args, **kwargs):
        self.object = UserOrganization.objects.get(code_activating=kwargs['pk'])
        self.object.status_active = 'A'
        self.object.save()
        return redirect('crm:invitemessage-index')

class InviteMessageLeave(LoginRequiredMixin, SessionMixin, DeleteView):
    model = UserOrganization
    success_url = reverse_lazy('crm:invitemessage-index')

    def delete(self, request, *args, **kwargs):
        self.object = UserOrganization.objects.get(code_activating=kwargs['pk'])
        success_url = self.get_success_url()
        user_account = self.object.user_account
        self.object.delete()

        if not UserOrganization.objects.filter(
                user_account=user_account).exists():
            user_account.delete()
        return HttpResponseRedirect(success_url)


class Help(LoginRequiredMixin, SessionMixin, TemplateView):
    template_name = 'crm/help_index.html'
