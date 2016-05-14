# coding:utf-8
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.UserLogin.as_view()),
    url(r'^logout/$', views.Logout.as_view()),
    url(r'^lista_usuarios/$', views.ListaUsuario.as_view()),
    url(r'^novo_usuario/$', views.CadastroUsuario.as_view()),
    url(r'^editar_usuario/$', views.CadastroUsuario.as_view()),
    url(r'^excluir_usuario/$', views.CadastroUsuario.as_view()),
    url(r'^redefinepwd/$', views.RedefinePassword.as_view()),
]
