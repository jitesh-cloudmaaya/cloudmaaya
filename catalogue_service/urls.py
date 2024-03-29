"""catalogue_service URL Configuration

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
from django.conf.urls import include, url
from django.contrib import admin
from rest_framework import routers, serializers, viewsets
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='Shopping Tool API')
admin.site.site_header = 'Allume Admin' # customize admin window title

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^admin/', include("massadmin.urls")),
    url(r'^product_api/', include('product_api.urls', namespace='v1')),
    url(r'', include('shopping_tool.urls', namespace='shopping_tool')),
    url(r'^shopping_tool_api/', include('shopping_tool_api.urls', namespace='shopping_tool_api')),
    url(r'^docs/', schema_view),
    # stylist management
    url(r'^management/', include('stylist_management.urls')),
]
