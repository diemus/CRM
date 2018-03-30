from django.conf.urls import url,include

from home import views

urlpatterns = [
    url(r'^$',views.index),
    url(r'^add$',views.add),
    url(r'^(?P<app_name>[a-zA-Z0-9]+)$',views.tables),
    url(r'^(?P<app_name>[a-zA-Z0-9]+)/(?P<table_name>[a-zA-Z0-9]+)$',views.table_data,name='table'),
    url(r'^(?P<app_name>[a-zA-Z0-9]+)/(?P<table_name>[a-zA-Z0-9]+)/(?P<nid>[a-zA-Z0-9]+)/edit$',views.edit,name='edit'),
    url(r'^(?P<app_name>[a-zA-Z0-9]+)/(?P<table_name>[a-zA-Z0-9]+)/delete',views.delete),
    url(r'^(?P<app_name>[a-zA-Z0-9]+)/(?P<table_name>[a-zA-Z0-9]+)/add$',views.add),
    url(r'^(?P<app_name>[a-zA-Z0-9]+)/(?P<table_name>[a-zA-Z0-9]+)/action',views.action),
]
