from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^organizations/$', views.OrganizationIndex.as_view(), name='organization_index'),
    url(r'^dashboard/$', views.Dashboard.as_view()),
]
