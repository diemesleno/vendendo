from django.conf.urls import url
from . import views

app_name = 'crm'

urlpatterns = [
    # /organization/2/delete/
    url(r'^organization/(?P<pk>[0-9]+)/delete/$', views.OrganizationDelete.as_view(), name='organization-delete'),
    # /organization/2/
    url(r'^organization/(?P<pk>[0-9]+)/$', views.OrganizationUpdate.as_view(), name='organization-update'),
    # /organization/add/
    url(r'^organization/add/$', views.OrganizationCreate.as_view(), name='organization-add'),

    url(r'^organizations/$', views.OrganizationIndex.as_view(), name='organization-index'),

    url(r'^sellers/$', views.SellerIndex.as_view(), name='seller-index'),
    
    url(r'^dashboard/$', views.Dashboard.as_view(), name='dashboard-index'),
]
