from django.conf.urls import url
from . import views

app_name = 'crm'

urlpatterns = [

    url(r'^organization/(?P<pk>[0-9]+)/delete/$', views.OrganizationDelete.as_view(), name='organization-delete'),
    url(r'^organization/(?P<pk>\d+)/$', views.OrganizationUpdate.as_view(), name='organization-update'),
    url(r'^organization/add/$', views.OrganizationCreate.as_view(), name='organization-add'),
    url(r'^organizations/$', views.OrganizationIndex.as_view(), name='organization-index'),

    url(r'^seller/(?P<pk>[0-9]+)/deactivate/$', views.SellerDeactivate.as_view(), name='seller-deactivate'),
    url(r'^seller/(?P<pk>[0-9]+)/activate/$', views.SellerActivate.as_view(), name='seller-activate'),
    url(r'^seller/(?P<pk>[0-9]+)/delete/$', views.SellerDelete.as_view(), name='seller-delete'),
    url(r'^seller/(?P<pk>[0-9]+)/toinvite/$', views.SellerInvite.as_view(), name='seller-invite'),
    url(r'^invite/activate/$', views.SellerInviteActivate.as_view(), name='seller-invite-activate'),
    url(r'^seller/find/$', views.SellerFind.as_view(), name='seller-find'),
    url(r'^seller/add/$', views.SellerCreate.as_view(), name='seller-add'),
    url(r'^seller/join/$', views.SellerJoin.as_view(), name='seller-join'),
    url(r'^sellers/$', views.SellerIndex.as_view(), name='seller-index'),

    url(r'^occupationarea/(?P<pk>[0-9]+)/delete/$', views.OccupationAreaDelete.as_view(), name='occupationarea-delete'),
    url(r'^occupationarea/(?P<pk>[0-9]+)/$', views.OccupationAreaUpdate.as_view(), name='occupationarea-update'),
    url(r'^occupationarea/add/$', views.OccupationAreaCreate.as_view(), name='occupationarea-add'),
    url(r'^occupationarea/$', views.OccupationAreaIndex.as_view(), name='occupationarea-index'),

    url(r'^customer/(?P<pk>[0-9]+)/delete/$', views.CustomerDelete.as_view(), name='customer-delete'),
    url(r'^customer/(?P<pk>[0-9]+)/$', views.CustomerUpdate.as_view(), name='customer-update'),
    url(r'^customer/add/$', views.CustomerCreate.as_view(), name='customer-add'),
    url(r'^customer/$', views.CustomerIndex.as_view(), name='customer-index'),

    url(r'^salestage/(?P<pk>[0-9]+)/delete/$', views.SaleStageDelete.as_view(), name='salestage-delete'),
    url(r'^salestage/(?P<pk>[0-9]+)/$', views.SaleStageUpdate.as_view(), name='salestage-update'),
    url(r'^salestage/add/$', views.SaleStageCreate.as_view(), name='salestage-add'),
    url(r'^salestage/$', views.SaleStageIndex.as_view(), name='salestage-index'),

    url(r'^dashboard/$', views.Dashboard.as_view(), name='dashboard-index'),

    url(r'^success/$', views.SuccessPage.as_view(), name='success-index'),
    url(r'^error/$', views.ErrorPage.as_view(), name='error-index'),
]
