# coding:utf-8
from django.shortcuts import render
from django.views.generic import base, TemplateView
from django.template.response import TemplateResponse
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .forms import NovoUsuarioForm
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from crm.models import Organization
import uuid
import hashlib


class ListaUsuario(base.View):
    template_name = "userapp/listar_usuarios.html"

    def get(self, request):
        usuarios = User.objects.all()
        titulo = 'Lista de Usuarios'
        return TemplateResponse(request,
                                self.template_name,
                                {'Usuarios': usuarios, 'Titulo': titulo})


class CadastroUsuario(base.View):
    template_name = "userapp/cadastro_usuario.html"
    form_class = NovoUsuarioForm
    titulo = 'Cadastro de Usuario'

    def get(self, request):
        id = request.GET.get('id', False)
        eid = request.GET.get('eid', False)
        if id:
            usuario = User.objects.get(id=id)
            return TemplateResponse(request,
                                    self.template_name,
                                    {'Titulo': self.titulo,
                                     'usuario': usuario})
        elif eid:
            usuario = User.objects.get(id=eid)
            usuario.delete()
            return HttpResponseRedirect("/")
        else:
            return TemplateResponse(request,
                                    self.template_name,
                                    {'Titulo': self.titulo})

    def post(self, request):
        id = request.POST.get('id', False)
        if id:
            usuario = User.objects.get(id=id)
            form = self.form_class(request.POST, instance=usuario)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect("/")
            else:
                return TemplateResponse(request,
                                        self.template_name,
                                        {'Titulo': self.titulo,
                                         'form': form,
                                         'usuario': usuario})
        else:
            usuario = User()
            form = self.form_class(request.POST, instance=usuario)
            if form.is_valid():
                u = form.save(commit=False)
                u.username = hashlib.md5(u.email).hexdigest()[-30:]
                u.save()
                organization = Organization()
                organization.user = u
                organization.name = request.POST['organization']
                organization.save()
                return HttpResponseRedirect("/")
            else:
                return TemplateResponse(request,
                                        self.template_name,
                                        {'Titulo': self.titulo,
                                         'form': form})


class UserLogin(base.View):
    template_name = "userapp/userlogin.html"
    titulo = 'Login'

    def get(self, request):
        return TemplateResponse(request,
                                self.template_name,
                                {'Titulo': self.titulo})

    def post(self, request):
        usuario = request.POST['username']
        senha = request.POST['password']
        user = authenticate(username=usuario, password=senha)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect("/lista_usuarios/")
            else:
                return TemplateResponse(request,
                                        self.template_name,
                                        {'Titulo': self.titulo,
                                         'erro': "A senha é válida, \
                                         mas o usuario está inativo"})
        else:
            return TemplateResponse(request,
                                    self.template_name,
                                    {'Titulo': self.titulo,
                                     'erro': "Usuário ou senha incorretos."})


class RedefinePassword(base.View):
    template_name = "userapp/redefinepwd.html"

    def get(self, request):
        return TemplateResponse(request,
                                self.template_name,
                                {})

    def post(self, request):
        email = request.POST['email']
        user = User.objects.filter(email=email)
        if user:
            user = user[0]
            if user.is_active:
                try:
                    salt = uuid.uuid4().hex
                    new_pass = str(hashlib.md5(salt.encode() + email.encode()).hexdigest())[-8:]
                    user.set_password(new_pass)
                    user.save()
                    subject = "Sua nova senha - Vendendo CRM"
                    body = "Olá "+str(user.first_name)+", <br /><br />Esta é a nova senha da sua conta "+str(email)+" no Vendendo CRM: <br /><b>"+str(new_pass)+"</b>"
                    send_mail(subject, body, "hostmaster@vendendo.com.br", [email], html_message=body)
                    return TemplateResponse(request,
                                            self.template_name,
                                            {'success': "Um e-mail foi enviado para você com \
                                            a sua nova senha"})
                except Exception, e:
                   return TemplateResponse(request,
                                           self.template_name,
                                           {'erro': "Erro interno: " + str(e.message)})
            else:
                return TemplateResponse(request,
                                        self.template_name,
                                        {'erro': "Este usuário encontra-se, \
                                         inativo. Entre em contato com o \
                                         administrador da conta."})
        else:
            return TemplateResponse(request,
                                    self.template_name,
                                    {'erro': "Não existe um usuário com este e-mail."})


class Logout(base.View):

    def get(self, request):
        logout(request)
        return HttpResponseRedirect("/")
