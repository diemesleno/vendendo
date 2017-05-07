from django.conf.urls import url
from . import views

app_name = 'landpage'

urlpatterns = [

    url(r'^$', views.LandPageIndex.as_view(), name='landpage-index'),
]
