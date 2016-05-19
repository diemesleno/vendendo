from django.shortcuts import render
from django.views.generic import base, TemplateView
from django.template.response import TemplateResponse
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin


class Dashboard(LoginRequiredMixin, base.View):

    template_name = 'crm/dashboard.html'

    def get(self, request):
      return TemplateResponse(request,
                              self.template_name,
                              {})
