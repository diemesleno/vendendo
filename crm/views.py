from django.shortcuts import render
from django.views.generic import base, TemplateView
from django.template.response import TemplateResponse
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from crm.models import UserOrganization
from userapp.models import UserComplement


class Dashboard(LoginRequiredMixin, base.View):

    template_name = 'crm/dashboard.html'

    def get(self, request):
        user_account = User.objects.get(id=request.user.id).id
        organizations = UserOrganization.objects.filter(user_account=user_account)
        organization_active = UserComplement.objects.get(user_account=user_account)
        type_user_organization = UserOrganization.objects.get(
                                    user_account=user_account, 
                                    organization=organization_active.organization_active_id).type_user
        return TemplateResponse(request,
                                self.template_name,
                                {'organizations': organizations,
                                 'type_user_organization': type_user_organization,
                                 'organization_active': organization_active,
                                 })
