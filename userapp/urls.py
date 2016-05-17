# coding:utf-8
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.UserLogin.as_view()),
    url(r'^logout/$', views.Logout.as_view()),
    url(r'^listusers/$', views.ListUsers.as_view()),
    url(r'^newuser/$', views.RegisterUser.as_view()),
    url(r'^edituser/$', views.RegisterUser.as_view()),
    url(r'^deleteuser/$', views.RegisterUser.as_view()),
    url(r'^resetpwd/$', views.ResetPassword.as_view()),
]
