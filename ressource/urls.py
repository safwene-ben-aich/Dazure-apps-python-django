from django.conf.urls import url
from . import views

app_name = 'ressource'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^register/$', views.register, name='register'),
    url(r'^login_user/$', views.login_user, name='login_user'),
    url(r'^(?P<ressource_id>[0-9]+)/$', views.detail, name='detail_ressource'),
    url(r'^logout_user/$', views.logout_user, name='logout_user'),
    url(r'^create_ressource/$', views.create_ressource, name='create_ressource'),
    url(r'^(?P<ressource_id>[0-9]+)/delete_ressource/$', views.delete_ressource, name='delete_ressource'),
    url(r'^(?P<ressource_id>[0-9]+)/create_storage/$', views.create_storage, name='create_storage'),
    url(r'^(?P<ressource_id>[0-9]+)/delete_storage/(?P<storage_id>[0-9]+)/$', views.delete_storage, name='delete_storage'),
    url(r'^(?P<ressource_id>[0-9]+)/create_vnet/$', views.create_vnet, name='create_vnet'),
    url(r'^(?P<ressource_id>[0-9]+)/delete_vnet/(?P<vnet_id>[0-9]+)/$', views.delete_vnet,name='delete_vnet'),
    url(r'^(?P<ressource_id>[0-9]+)/create_subnet/$', views.create_subnet, name='create_subnet'),
    url(r'^(?P<ressource_id>[0-9]+)/delete_subnet/(?P<subnet_id>[0-9]+)/$', views.delete_subnet, name='delete_subnet'),
    url(r'^(?P<ressource_id>[0-9]+)/create_nic/$', views.create_nic, name='create_nic'),
    url(r'^(?P<ressource_id>[0-9]+)/delete_nic/(?P<nic_id>[0-9]+)/$', views.delete_nic, name='delete_nic'),
    url(r'^(?P<ressource_id>[0-9]+)/create_virtualMachine/$', views.create_virtualMachine, name='create_virualMachine'),
    url(r'^(?P<ressource_id>[0-9]+)/delete_virtualMachine/(?P<virtualMachine_id>[0-9]+)/$', views.delete_virtualMachine, name='delete_virtualMachine'),
    url(r'^(?P<ressource_id>[0-9]+)/automation/(?P<operation_id>[0-9]+)/$', views.automation, name='automation')
    ]