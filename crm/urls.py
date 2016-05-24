from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^organizations/$', views.Organizations.as_view()),
    url(r'^dashboard/$', views.Dashboard.as_view()),
]
