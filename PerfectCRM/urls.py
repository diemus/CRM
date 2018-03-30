"""PerfectCRM URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin

from home import views as home_views
from account import views as account_views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import login

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^king_admin/',include('home.urls')),
    url(r'^crm/',include('crm.urls')),
    url(r'^$',home_views.index),
    url(r'^login$',account_views.LoginView.as_view(),name='login'),
    url(r'^logout$',account_views.logout_view,name='logout'),
    url(r'^password_change$',account_views.PasswordChangeView.as_view(),name='password_change'),
    url(r'^global_password_change$',account_views.GlobalPasswordChangeView.as_view(),name='global_password_change'),
    url(r'^test',account_views.test),

]
