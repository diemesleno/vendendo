# coding:utf-8
from django.shortcuts import render
from django.views.generic import base, TemplateView
from django.template.response import TemplateResponse
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .forms import NewUserForm
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from crm.models import Organization, UserOrganization
from .models import UserComplement
import uuid
import hashlib


class ListUsers(base.View):
    template_name = "userapp/listusers.html"

    def get(self, request):
        users = User.objects.all()
        title = 'Lista de Usuários'
        return TemplateResponse(request,
                                self.template_name,
                                {'users': users, 'title': title})


class RegisterUser(base.View):
    template_name = "userapp/registeruser.html"
    form_class = NewUserForm
    title = 'Cadastro de Usuário'

    def get(self, request):
        id = request.GET.get('id', False)
        eid = request.GET.get('eid', False)
        if id:
            user_account = User.objects.get(id=id)
            return TemplateResponse(request,
                                    self.template_name,
                                    {'title': self.title,
                                     'user_account': user_account})
        elif eid:
            user_account = User.objects.get(id=eid)
            user_account.delete()
            return HttpResponseRedirect("/")
        else:
            return TemplateResponse(request,
                                    self.template_name,
                                    {'title': self.title})

    def post(self, request):
        id = request.POST.get('id', False)
        if id:
            user_account = User.objects.get(id=id)
            form = self.form_class(request.POST, instance=user_account)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect("/")
            else:
                return TemplateResponse(request,
                                        self.template_name,
                                        {'title': self.title,
                                         'form': form,
                                         'user_account': user_account})
        else:
            user_account = User()
            form = self.form_class(request.POST, instance=user_account)
            if form.is_valid():
                if not User.objects.filter(email=request.POST['email']).exists():
                    u = form.save(commit=False)
                    u.username = hashlib.md5(u.email).hexdigest()[-30:]
                    u.set_password(request.POST['password'])
                    u.save()
                    organization = Organization()
                    organization.user_account = u
                    organization.name = request.POST['organization']
                    organization.save()
                    uc = UserComplement()
                    uc.user_account = u
                    uc.organization_active = organization
                    uc.save()
                    user_organization = UserOrganization()
                    user_organization.user_account = u
                    user_organization.organization = organization
                    user_organization.type_user = 'A'
                    user_organization.save()
                    return HttpResponseRedirect("/")
                else:
                    return TemplateResponse(request,
                                            self.template_name,
                                            {'title': self.title,
                                             'form': form,
                                             'error':"Já existe uma conta registrada com esse e-mail."})
            else:
                return TemplateResponse(request,
                                        self.template_name,
                                        {'title': self.title,
                                         'form': form})


class UserLogin(base.View):
    template_name = "userapp/userlogin.html"
    title = 'Entrar'

    def get(self, request):
        return TemplateResponse(request,
                                self.template_name,
                                {'title': self.title})

    def post(self, request):
        email = request.POST['email']
        print email
        password = request.POST['password']
        print password
        username = hashlib.md5(email).hexdigest()[-30:]
        print username
        user_account = authenticate(username=username, password=password)
        if user_account is not None:
            if user_account.is_active:
                login(request, user_account)
                return HttpResponseRedirect("/dashboard/")
            else:
                return TemplateResponse(request,
                                        self.template_name,
                                        {'title': self.title,
                                         'error': "Este usuário encontra-se, \
                                          inativo. Entre em contato com o \
                                          administrador da conta."})
        else:
            return TemplateResponse(request,
                                    self.template_name,
                                    {'title': self.title,
                                     'error': "E-mail ou senha incorretos."})


class ResetPassword(base.View):
    template_name = "userapp/resetpwd.html"

    def get(self, request):
        return TemplateResponse(request,
                                self.template_name,
                                {})

    def post(self, request):
        email = request.POST['email']
        user_account = User.objects.filter(email=email)
        if user_account:
            user_account = user_account[0]
            if user_account.is_active:
                try:
                    salt = uuid.uuid4().hex
                    new_pass = str(hashlib.md5(salt.encode() + email.encode()).hexdigest())[-8:]
                    user_account.set_password(new_pass)
                    user_account.save()
                    subject = "Sua nova senha - Vendendo CRM"
                    body = "Olá "+str(user_account.first_name)+", <br /><br />Esta é a \
                    nova senha da sua conta "+str(email)+" no Vendendo CRM: \
                    <br /><b>"+str(new_pass)+"</b>"
                    send_mail(subject, body, "hostmaster@vendendo.com.br",
                    [email], html_message=body)
                    return TemplateResponse(request,
                                            self.template_name,
                                            {'success': "Um e-mail foi enviado para você com \
                                            a sua nova senha"})
                except Exception, e:
                   return TemplateResponse(request,
                                           self.template_name,
                                           {'error': "Erro interno: " + str(e.message)})
            else:
                return TemplateResponse(request,
                                        self.template_name,
                                        {'error': "Este usuário encontra-se, \
                                         inativo. Entre em contato com o \
                                         administrador da conta."})
        else:
            return TemplateResponse(request,
                                    self.template_name,
                                    {'error': "Não existe um usuário com este \
                                    e-mail."})


class Logout(base.View):

    def get(self, request):
        logout(request)
        return HttpResponseRedirect("/")
