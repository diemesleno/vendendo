# coding:utf-8
from django.shortcuts import render
from django.views.generic import base, ListView, CreateView, UpdateView, \
    DeleteView, TemplateView, FormView
from django.template.response import TemplateResponse
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from crm.models import Organization, UserOrganization, OccupationArea, \
                       Customer, SaleStage, CustomerService, Opportunity, \
                       OpportunityItem, Activity, Contact
from crm.forms import OrganizationForm, MemberFindForm, MemberForm, \
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
from operator import itemgetter
from xlrd import open_workbook
#import pyexcel as pe 
import uuid
import hashlib
import locale
import pytz
import json
locale.setlocale(locale.LC_ALL, 'pt_BR')


class Sendx(object):

    @staticmethod
    def send_invite(self, user_organization):
        try:
            header = '<div id="header" style="width:100%;"> <img src="http://www.vendendocrm.com/static/images/vendendo_logo_mini.png"> <div><div id="content" style="font-family:helvetica, arial, sans-serif; font-size:14px; font-weight: 300;"><br>'
            footer = '</div> <div id="footer" style="width:100%; color:#1abc9c; text-align: left; font-family:Helvetica; font-size:small;"> <a href="http://www.vendendocrm.com" style="text-decoration:underline; color:#1abc9c;">www.vendendocrm.com</a><br> </div> <div style="margin-top:5px;"> <a href="https://www.facebook.com/Vendendo-CRM-1821057294879669/"><img src="http://www.vendendocrm.com/static/images/facebook_icon.png" width="24" height="24"></a> <a href="http://twitter.com/vendendocrm"><img src="http://www.vendendocrm.com/static/images/tweet_icon.png" width="24" height="24"></a> <a href="http://www.youtube.com/channel/UCzotKDjwHxykwGmv8TstxhA"><img src="http://www.vendendocrm.com/static/images/youtube_icon.png" width="24" height="24"></a> </div>'
            subject = "Você foi convidado! Vendendo CRM"
            body = "<p>Olá "+str(user_organization.user_account.first_name)+", <br /><br />Você foi convidado por <b>"+str(self.request.user.first_name)+"</b> para ser um de seus membros na <b>"+str(user_organization.organization)+"</b>. <br /><br /> Clique no link a seguir para aceitar o convite: <br /><a href='"+str(settings.INVITE_HOST)+"/invite/activate/?code="+str(user_organization.code_activating)+"'>"+str(settings.INVITE_HOST)+"/invite/activate/?code="+str(user_organization.code_activating)+"</a></p>"
            body = header + body + footer
            send_mail(subject, body, "Vendendo CRM <do-not-reply@vendendocrm.com>",
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
            if type_user_organization == "A" or type_user_organization == "M":
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
        context['customers_potential_count'] = self.get_customers_potential_count()
        context['opportunities_open_count'] = self.get_opportunities_open_count()
        context['customers_base_count'] = Customer.objects.filter(organization=self.organization_active, category='P').count()
        context['customers_base_top5'] = Customer.objects.filter(organization=self.organization_active, category='P').order_by('-relevance')[:5]
        context['customers_potential_complete'] = range(context['customers_potential_count'], 5)
        context['opportunities_open_complete'] = range(context['opportunities_open_count'], 5)
        context['customers_base_complete'] = range(context['customers_base_count'], 5)
        context['opportunity_value_stages'] = self.get_opportunity_value_stages()
        context['customers_by_category'] = self.get_customers_by_category()
        context['segments_by_value'] = self.get_segments_by_value()
        context['new_deals'] = self.get_new_deals()
        context['lost_deals'] = self.get_lost_deals()
        context['won_deals'] = self.get_won_deals()
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

    def get_opportunities_open_count(self):
        if self.is_admin:
            result = Opportunity.objects.filter(organization=self.organization_active,
                                                stage__final_stage=False).count()
        else:
            result = Opportunity.objects.filter(organization=self.organization_active,
                                                stage__final_stage=False,
                                                seller=self.user_account).count()
        return result

    def get_customers_potential_count(self):
        if self.is_admin:
            result = Customer.objects.filter(Q(opportunity__isnull=True, category__in=['Q']) | Q(opportunity__stage__final_stage=True, category__in=['P']),
                                             organization=self.organization_active).count()
        else:
            result = Customer.objects.filter(Q(opportunity__isnull=True, category__in=['Q']) | Q(opportunity__stage__final_stage=True, category__in=['P']),
                                             organization=self.organization_active,
                                             responsible_seller=self.user_account).count()
        return result

    def get_opportunity_value_stages(self):
        # calculate opportunity values by stage
        stages = SaleStage.objects.filter(organization=self.organization_active, final_stage=False).order_by('order_number')
        opportunity_value_stages = "["
        idx = 0
        for stage in stages:
            opportunity_value = stage.get_opportunity_value_by_type_user(is_admin=self.is_admin, user_account=self.user_account)
            if opportunity_value > 0:
                if idx > 0:
                    opportunity_value_stages += ","
                opportunity_value_stages += "['%s', %s]" % (stage.name, str(opportunity_value))
                idx += 1
        opportunity_value_stages += "]"
        return opportunity_value_stages

    def get_customers_by_category(self):
        if self.is_admin:
            qualified_customers = Customer.objects.filter(Q(opportunity__isnull=True, category__in=['Q']) | Q(opportunity__stage__final_stage=True, category__in=['P']),
                                                          organization=self.organization_active).count()
        else:
            qualified_customers = Customer.objects.filter(Q(opportunity__isnull=True, category__in=['Q']) | Q(opportunity__stage__final_stage=True, category__in=['P']),
                                                          organization=self.organization_active,
                                                          responsible_seller=self.user_account).count()
        not_qualified_customers = Customer.objects.filter(Q(opportunity__isnull=True) | Q(opportunity__stage__final_stage=True),
                                                          organization=self.organization_active,
                                                          category='U').count()
        result = "[{name: 'Qualificados', y: %s }, {name: 'Não qualificados', y: %s }]" % (qualified_customers, not_qualified_customers)
        return result

    def get_segments_by_value(self):
        customers = Customer.objects.filter(organization=self.organization_active, category='P')
        customers_and_value = [{'name':customer.occupationarea.name, 'value':customer.opportunities_won_value} for customer in customers]
        result = self.building_list(customers_and_value)
        return result

    def building_list(self, sorted_trees):
        summary_trees = []
        for item in sorted_trees:
            if not item['name'] in [k[0] for k in summary_trees]:
                summary_trees.append([item['name'], sum(i['value'] for i in sorted_trees if i['name'] == item['name'])])
        result = "["
        for idx, item in enumerate(sorted(summary_trees, key=itemgetter(1), reverse=True)[:5]):
            if idx > 0:
                result += ","
            result += "['%s', %s]" % (item[0], str(item[1]))
        result += "]"
        return result

    def get_new_deals(self):
        current_year = datetime.today().year
        current_month = datetime.today().month
        if self.is_admin:
            opportunities = Opportunity.objects.filter(organization=self.organization_active,
                                                       created__year__gte=current_year,
                                                       created__month__gte=current_month,
                                                       stage__final_stage=False)
        else:
            opportunities = Opportunity.objects.filter(organization=self.organization_active,
                                                       created__year__gte=current_year,
                                                       created__month__gte=current_month,
                                                       stage__final_stage=False,
                                                       seller=self.user_account)
        result = 0
        for opportunity in opportunities:
            result += opportunity.expected_value
        result = locale.currency(result, grouping=True, symbol=None)
        return result

    def get_lost_deals(self):
        current_year = datetime.today().year
        current_month = datetime.today().month
        if self.is_admin:
            opportunities = Opportunity.objects.filter(organization=self.organization_active,
                                                       created__year__gte=current_year,
                                                       created__month__gte=current_month,
                                                       stage__final_stage=True,
                                                       stage__conclusion='L')
        else:
            opportunities = Opportunity.objects.filter(organization=self.organization_active,
                                                       created__year__gte=current_year,
                                                       created__month__gte=current_month,
                                                       stage__final_stage=True,
                                                       stage__conclusion='L',
                                                       seller=self.user_account)
        result = 0
        for opportunity in opportunities:
            result += opportunity.expected_value
        result = locale.currency(result, grouping=True, symbol=None)
        return result

    def get_won_deals(self):
        current_year = datetime.today().year
        current_month = datetime.today().month
        if self.is_admin:
            opportunities = Opportunity.objects.filter(organization=self.organization_active,
                                                       created__year__gte=current_year,
                                                       created__month__gte=current_month,
                                                       stage__final_stage=True,
                                                       stage__conclusion='W')
        else:
            opportunities = Opportunity.objects.filter(organization=self.organization_active,
                                                       created__year__gte=current_year,
                                                       created__month__gte=current_month,
                                                       stage__final_stage=True,
                                                       stage__conclusion='W',
                                                       seller=self.user_account)
        result = 0
        for opportunity in opportunities:
            result += opportunity.expected_value
        result = locale.currency(result, grouping=True, symbol=None)
        return result

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


# Member Views
class MemberSecMixin(object):

    def dispatch(self, *args, **kwargs):
        user = self.request.user
        organization = UserOrganization.objects.get(
                                pk=self.kwargs['pk']).organization

        if not UserOrganization.objects.filter(user_account=user,
                                               organization=organization,
                                               type_user__in=['A','M']).exists():
            return redirect('crm:dashboard-index')
        return super(MemberSecMixin, self).dispatch(*args, **kwargs)


class MemberUserSecMixin(object):

    def dispatch(self, *args, **kwargs):
        if not UserOrganization.objects.filter(user_account=self.user_account,
                                               organization=self.organization_active,
                                               type_user__in=['A','M']).exists():
            return redirect('crm:dashboard-index')
        return super(MemberUserSecMixin, self).dispatch(*args, **kwargs)


class MemberIndex(LoginRequiredMixin, SessionMixin, MemberUserSecMixin, ListView):
    template_name = 'crm/member_index.html'
    context_object_name = 'members'

    def get_queryset(self):
        user_account = User.objects.get(id=self.request.user.id).id
        organization_active = UserComplement.objects.get(
                                user_account=user_account).organization_active
        return UserOrganization.objects.filter(
            organization=organization_active, type_user__in=['S', 'M'])


class MemberFind(LoginRequiredMixin, SessionMixin, FormView):
    template_name = 'crm/member_find_form.html'
    form_class = MemberFindForm

    def get_form_kwargs(self):
        kwargs = super(MemberFind, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        self.request.session['email_find'] = form.cleaned_data['email']
        # Verify if new e-mail
        if User.objects.filter(email=form.cleaned_data['email']).exists():
            self.success_url = reverse_lazy('crm:member-join')
        else:
            # Create Member
            self.success_url = reverse_lazy('crm:member-add')
        return super(MemberFind, self).form_valid(form)


class MemberCreate(LoginRequiredMixin, SessionMixin, CreateView):
    model = UserOrganization
    template_name = 'crm/member_form.html'
    success_url = reverse_lazy('crm:member-index')
    form_class = MemberForm

    def get_context_data(self, **kwargs):
        context = super(MemberCreate, self).get_context_data(**kwargs)
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
        return super(MemberCreate, self).form_valid(form)


class MemberJoin(LoginRequiredMixin, SessionMixin, CreateView):
    model = UserOrganization
    template_name = 'crm/member_join_form.html'
    success_url = reverse_lazy('crm:member-index')
    fields = []

    def get_context_data(self, **kwargs):
        context = super(MemberJoin, self).get_context_data(**kwargs)
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
        return super(MemberJoin, self).form_valid(form)


class MemberDeactivate(LoginRequiredMixin, SessionMixin,
                       MemberSecMixin, UpdateView):
    model = UserOrganization

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.status_active = 'I'
        self.object.save()
        return redirect('crm:member-index')


class MemberActivate(LoginRequiredMixin, SessionMixin,
                     MemberSecMixin, UpdateView):
    model = UserOrganization

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.status_active = 'A'
        self.object.save()
        return redirect('crm:member-index')


class MemberAlterType(LoginRequiredMixin, SessionMixin,
                      MemberSecMixin, UpdateView):
    model = UserOrganization

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.type_user == 'M':
            self.object.type_user = 'S'
        elif self.object.type_user == 'S':
            self.object.type_user = 'M'
        self.object.save()
        return redirect('crm:member-index')


class MemberDelete(LoginRequiredMixin, SessionMixin,
                   MemberSecMixin, DeleteView):
    model = UserOrganization
    success_url = reverse_lazy('crm:member-index')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        user_account = self.object.user_account
        self.object.delete()

        if not UserOrganization.objects.filter(
                user_account=user_account).exists():
            user_account.delete()
        return HttpResponseRedirect(success_url)


class MemberInviteActivate(base.View):

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


class MemberInvite(LoginRequiredMixin, SessionMixin,
                   MemberSecMixin, UpdateView):
    model = UserOrganization

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        Sendx.send_invite(self, self.object)
        return redirect('crm:member-index')


# Occupation Area Views
class OccupationAreaSecMixin(object):

    def dispatch(self, *args, **kwargs):
        u = self.request.user
        oa = OccupationArea.objects.get(pk=self.kwargs['pk'])
        occupation_area_organization = oa.organization

        user_of_organization = UserOrganization.objects.filter(user_account=self.user_account,
                                                               organization=occupation_area_organization).exists()
        if not user_of_organization or occupation_area_organization != self.organization_active:
            return redirect('crm:error-index')
        return super(OccupationAreaSecMixin, self).dispatch(*args, **kwargs)


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

    def get_form_kwargs(self):
        kwargs = super(OccupationAreaCreate, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        occupation_area = form.save(commit=False)
        user_account = User.objects.get(id=self.request.user.id).id
        organization_active = UserComplement.objects.get(
                                 user_account=user_account).organization_active
        occupation_area.organization = organization_active
        occupation_area.save()
        return super(OccupationAreaCreate, self).form_valid(form)


class OccupationAreaUpdate(LoginRequiredMixin, SessionMixin, OccupationAreaSecMixin, UpdateView):
    model = OccupationArea
    form_class = OccupationAreaForm

    def get_form_kwargs(self):
        kwargs = super(OccupationAreaUpdate, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs


class OccupationAreaDelete(LoginRequiredMixin, SessionMixin, OccupationAreaSecMixin, DeleteView):
    model = OccupationArea
    success_url = reverse_lazy('crm:occupationarea-index')


# Customer Area Views
class CutomerSecMixin(object):

    def dispatch(self, *args, **kwargs):
        u = self.request.user
        c = Customer.objects.get(pk=self.kwargs['pk'])
        customer_organization = c.organization

        user_of_organization = UserOrganization.objects.filter(user_account=self.user_account,
                                                               organization=customer_organization).exists()
        if not user_of_organization or customer_organization != self.organization_active:
            return redirect('crm:error-index')
        return super(CutomerSecMixin, self).dispatch(*args, **kwargs)


class CustomerIndex(LoginRequiredMixin, SessionMixin, ListView):
    template_name = 'crm/customer_index.html'
    context_object_name = 'my_customers'

    def get_queryset(self):
        if self.is_admin:
            customers = Customer.objects.filter(organization=self.organization_active)
        else:
            customers = Customer.objects.filter(Q(category='U') | Q(category__in=['Q','P']) & Q(responsible_seller=self.user_account),
                                                organization=self.organization_active)
        return customers


class CustomerCreate(LoginRequiredMixin, SessionMixin, CreateView):
    model = Customer
    form_class = CustomerForm

    def form_valid(self, form):
        customer = form.save(commit=False)
        customer.organization = self.organization_active
        customer.responsible_seller = self.user_account
        customer.save()
        user_complement = UserComplement.objects.get(
                                 user_account=self.user_account,
                                 organization_active=self.organization_active)
        user_complement.customers.add(customer)
        user_complement.save()
        # contacts
        self.save_contacts(customer=customer)
        return super(CustomerCreate, self).form_valid(form)

    def save_contacts(self, customer):
        contacts_name = self.request.POST.getlist('contact_name')
        contacts_email = self.request.POST.getlist('contact_email')
        contacts_tel = self.request.POST.getlist('contact_tel')
        contacts_position = self.request.POST.getlist('contact_position')
        # clear contacts
        Contact.objects.filter(customer=customer).delete()
        # create news contacts
        if contacts_name:
            for idx,contact_name in enumerate(contacts_name):
                contact_item = Contact()
                contact_item.customer = customer
                contact_item.contact_name = contact_name
                contact_item.contact_email = contacts_email[idx]
                contact_item.contact_tel = contacts_tel[idx]
                contact_item.contact_position = contacts_position[idx]
                contact_item.save()

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(organization=self.organization_active,
                          **self.get_form_kwargs())


class CustomerUpdate(LoginRequiredMixin, SessionMixin, CutomerSecMixin, UpdateView):
    model = Customer
    form_class = CustomerForm

    def get_context_data(self, **kwargs):
        context = super(CustomerUpdate, self).get_context_data(**kwargs)
        contacts = Contact.objects.filter(customer=self.kwargs['pk'])
        context['contacts'] = contacts
        return context

    def form_valid(self, form):
        customer = form.save(commit=False)
        if not self.is_admin:
            customer.responsible_seller = self.user_account
        customer.save()
        # contacts
        self.save_contacts(customer=customer)
        return super(CustomerUpdate, self).form_valid(form)

    def save_contacts(self, customer):
        contacts_name = self.request.POST.getlist('contact_name')
        contacts_email = self.request.POST.getlist('contact_email')
        contacts_tel = self.request.POST.getlist('contact_tel')
        contacts_position = self.request.POST.getlist('contact_position')
        # clear contacts
        Contact.objects.filter(customer=customer).delete()
        # create news contacts
        if contacts_name:
            for idx,contact_name in enumerate(contacts_name):
                contact_item = Contact()
                contact_item.customer = customer
                contact_item.contact_name = contact_name
                contact_item.contact_email = contacts_email[idx]
                contact_item.contact_tel = contacts_tel[idx]
                contact_item.contact_position = contacts_position[idx]
                contact_item.save()

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(organization=self.organization_active,
                          **self.get_form_kwargs())


class CustomerDelete(LoginRequiredMixin, SessionMixin, CutomerSecMixin, DeleteView):
    model = Customer
    success_url = reverse_lazy('crm:customer-index')


class CustomerImport(LoginRequiredMixin, SessionMixin, base.View):

    def post(self, request):
        output = json.loads('{"valid":true, "messages":[], "imported":false}')
        file_upload = request.FILES.get('file_upload', False)
        if file_upload:
            try:
                book = open_workbook(file_contents=file_upload.read())
                sheet = book.sheet_by_index(0)
                num_cols = sheet.ncols
                import_file = self.sheet_validate(output=output, sheet=sheet)
                print import_file
                if import_file['valid']:
                    for row_idx in range(1, sheet.nrows):
                        self.customer_add(sheet=sheet, row_idx=row_idx)
                    import_file['imported'] = True

                return HttpResponse(json.dumps(import_file))
            except:
                output['valid'] = False
                message_str = '{"line":"", "message":"%s"}' % ("Erro interno.")
                message = json.loads(message_str)
                output['messages'].append(message)
                return HttpResponse(json.dumps(import_file))
        else:
            output['valid'] = False
            message_str = '{"line":"", "message":"%s"}' % ("Arquivo não encontrado")
            message = json.loads(message_str)
            output['messages'].append()
            return HttpResponse(json.dumps(import_file))

    def sheet_validate(self, output, sheet):
        if sheet.nrows > 1:
            for row_idx in range(1, sheet.nrows):
                # customer name
                if sheet.cell(row_idx, 0).value == '':
                    output['valid'] = False
                    message_str = '{"line":"%s", "message":"%s"}' % (str(row_idx), "Nome do cliente não informado")
                    message = json.loads(message_str)
                    output['messages'].append(message)
                # customer name
                if sheet.cell(row_idx, 1).value == '':
                    output['valid'] = False
                    message_str = '{"line":"%s", "message":"%s"}' % (str(row_idx), "Segmento não informado")
                    message = json.loads(message_str)
                    output['messages'].append(message)
        else:
            output['valid'] = False
            message_str = '{"line":"", "message":"%s"}' % ("Arquivo de importação vazio")
            message = json.loads(message_str)
            output['messages'].append(message)
        return output

    def customer_add(self, sheet, row_idx):
        # Customer add
        customer = Customer()
        customer.name = sheet.cell(row_idx, 0).value
        customer.category = 'U'
        if OccupationArea.objects.filter(organization=self.organization_active,name=sheet.cell(row_idx, 1).value).exists():
            customer.occupationarea = OccupationArea.objects.get(organization=self.organization_active,name=sheet.cell(row_idx, 1).value)
        else:
            occupation_area = OccupationArea()
            occupation_area.organization = self.organization_active
            occupation_area.name = sheet.cell(row_idx, 1).value
            occupation_area.save()
            customer.occupationarea = occupation_area
        customer.organization = self.organization_active
        customer.responsible_seller = self.user_account
        customer.save()
        # Contact 1 add
        if sheet.cell(row_idx, 3).value != '':
            contact = Contact()
            contact.customer = customer
            contact.contact_name = sheet.cell(row_idx, 3).value
            contact.contact_email = sheet.cell(row_idx, 4).value
            contact.contact_tel = sheet.cell(row_idx, 5).value
            contact.contact_position = sheet.cell(row_idx, 6).value
            contact.save()
        # Contact 2 add
        if sheet.cell(row_idx, 7).value != '':
            contact = Contact()
            contact.customer = customer
            contact.contact_name = sheet.cell(row_idx, 7).value
            contact.contact_email = sheet.cell(row_idx, 8).value
            contact.contact_tel = sheet.cell(row_idx, 9).value
            contact.contact_position = sheet.cell(row_idx, 10).value
            contact.save()
        return customer


# SaleStage Views
class SaleStageSecMixin(object):

    def dispatch(self, *args, **kwargs):
        u = self.request.user
        ss = SaleStage.objects.get(pk=self.kwargs['pk'])
        sale_stage_organization = ss.organization

        user_of_organization = UserOrganization.objects.filter(user_account=self.user_account,
                                                               organization=sale_stage_organization).exists()
        if not user_of_organization or sale_stage_organization != self.organization_active:
            return redirect('crm:error-index')
        return super(SaleStageSecMixin, self).dispatch(*args, **kwargs)


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


class SaleStageUpdate(LoginRequiredMixin, SessionMixin, SaleStageSecMixin, UpdateView):
    model = SaleStage
    form_class = SaleStageForm


class SaleStageDelete(LoginRequiredMixin, SessionMixin, SaleStageSecMixin, DeleteView):
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


class SaleStageUp(LoginRequiredMixin, SessionMixin, SaleStageSecMixin, UpdateView):
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


class SaleStageDown(LoginRequiredMixin, SessionMixin, SaleStageSecMixin, UpdateView):
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
        o = Opportunity.objects.get(pk=self.kwargs['pk'])
        opportunity_organization = o.organization

        if self.is_admin:
            user_of_organization = UserOrganization.objects.filter(user_account=self.user_account,
                                                                   organization=opportunity_organization).exists()
            if not user_of_organization or opportunity_organization != self.organization_active:
                return redirect('crm:error-index')
        else:
            user_of_organization = UserOrganization.objects.filter(user_account=self.user_account,
                                                                   organization=opportunity_organization).exists()
            user_is_owner_of_opportunity = True if o.seller == self.user_account else False
            if not user_of_organization or opportunity_organization != self.organization_active or not user_is_owner_of_opportunity:
                return redirect('crm:error-index')
        return super(OpportunitySecMixin, self).dispatch(*args, **kwargs)


class OpportunityIndex(LoginRequiredMixin, SessionMixin, ListView):
    template_name = 'crm/opportunity_index.html'
    context_object_name = 'my_opportunities'

    def get_queryset(self):
        user_account = User.objects.get(id=self.request.user.id)
        organization_active = UserComplement.objects.get(
                                user_account=user_account).organization_active
        if self.is_admin:
            return Opportunity.objects.filter(organization=organization_active)
        else:
            return Opportunity.objects.filter(organization=organization_active, seller=self.user_account)


class OpportunityCreate(LoginRequiredMixin, SessionMixin, CreateView):
    model = Opportunity
    form_class = OpportunityForm

    def get_context_data(self, **kwargs):
        context = super(OpportunityCreate, self).get_context_data(**kwargs)
        user_account = User.objects.get(id=self.request.user.id)
        organization_active = UserComplement.objects.get(
                                user_account=user_account).organization_active
        customer_services = CustomerService.objects.filter(
                                organization=organization_active, status='A')
        context['customer_services'] = customer_services
        return context

    def form_valid(self, form):
        opportunity = form.save(commit=False)
        user_account = User.objects.get(id=self.request.user.id)
        organization_active = UserComplement.objects.get(
                                 user_account=user_account).organization_active
        opportunity.organization = organization_active
        if not self.is_admin:
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
                opportunity_item.expected_value = locale.atof(expected_values[idx])
                opportunity_item.expected_amount = locale.atof(expected_amounts[idx])
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
                                organization=organization_active, status='A')
        opportunity = Opportunity.objects.get(pk=self.kwargs['pk'])
        opportunity_items = OpportunityItem.objects.filter(
                                organization=organization_active,
                                opportunity=opportunity)
        context['customer_services'] = customer_services
        context['opportunity_items'] = opportunity_items
        return context

    def form_valid(self, form):
        opportunity = form.save()
        if not self.is_admin:
            opportunity.seller = self.user_account
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
                opportunity_item.expected_value = locale.atof(expected_values[idx])
                opportunity_item.expected_amount = locale.atof(expected_amounts[idx])
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
class ActivitySecMixin(object):

    def dispatch(self, *args, **kwargs):
        u = self.request.user
        a = Activity.objects.get(pk=self.kwargs['pk'])
        activity_organization = a.organization

        user_of_organization = UserOrganization.objects.filter(user_account=self.user_account,
                                                               organization=activity_organization).exists()
        if not user_of_organization or activity_organization != self.organization_active:
            return redirect('crm:error-index')
        return super(ActivitySecMixin, self).dispatch(*args, **kwargs)


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
                          user=self.user_account,
                          **self.get_form_kwargs())


class ActivityUpdate(LoginRequiredMixin, SessionMixin, ActivitySecMixin, UpdateView):
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
                          user=self.user_account,
                          **self.get_form_kwargs())


class ActivityDelete(LoginRequiredMixin, SessionMixin, ActivitySecMixin, DeleteView):
    model = Activity
    success_url = reverse_lazy('crm:activity-index')


# Invite messages Views
class InviteMessageIndex(LoginRequiredMixin, SessionMixin, ListView):
    template_name = 'crm/invite_message_index.html'
    context_object_name = 'my_messages'

    def get_queryset(self):
        user_account = User.objects.get(id=self.request.user.id)
        return UserOrganization.objects.filter(user_account=user_account).exclude(type_user='A')


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
