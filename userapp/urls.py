# coding:utf-8
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^login/$', views.UserLogin.as_view()),
    url(r'^logout/$', views.Logout.as_view()),
    url(r'^newuser/$', views.RegisterUser.as_view()),
    url(r'^edituser/$', views.EditUser.as_view()),
    # url(r'^deleteuser/$', views.RegisterUser.as_view()),
    url(r'^resetpwd/$', views.ResetPassword.as_view()),
    url(r'^editpwd/$', views.EditPassword.as_view()),
]
