# coding:utf-8
from django.shortcuts import render
from django.views.generic import base, TemplateView
from django.template.response import TemplateResponse
from django.contrib.auth.models import User
from .forms import NovoUsuarioForm
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from crm.models import Organization
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


class Logout(base.View):

    def get(self, request):
        logout(request)
        return HttpResponseRedirect("/")
