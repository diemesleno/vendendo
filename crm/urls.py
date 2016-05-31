from django.conf.urls import url
from . import views

app_name = 'crm'

urlpatterns = [

    url(r'^organization/(?P<pk>[0-9]+)/delete/$', views.OrganizationDelete.as_view(), name='organization-delete'),
    url(r'^organization/(?P<pk>[0-9]+)/$', views.OrganizationUpdate.as_view(), name='organization-update'),
    url(r'^organization/add/$', views.OrganizationCreate.as_view(), name='organization-add'),
    url(r'^organizations/$', views.OrganizationIndex.as_view(), name='organization-index'),

    url(r'^seller/(?P<pk>[0-9]+)/deactivate/$', views.SellerDeactivate.as_view(), name='seller-deactivate'),
    url(r'^seller/(?P<pk>[0-9]+)/activate/$', views.SellerActivate.as_view(), name='seller-activate'),
    url(r'^seller/(?P<pk>[0-9]+)/delete/$', views.SellerDelete.as_view(), name='seller-delete'),
    url(r'^seller/find/$', views.SellerFind.as_view(), name='seller-find'),
    url(r'^seller/add/$', views.SellerCreate.as_view(), name='seller-add'),
    url(r'^seller/join/$', views.SellerJoin.as_view(), name='seller-join'),
    url(r'^sellers/$', views.SellerIndex.as_view(), name='seller-index'),
    
    url(r'^dashboard/$', views.Dashboard.as_view(), name='dashboard-index'),
]
