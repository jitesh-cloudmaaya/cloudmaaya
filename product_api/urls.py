from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^basic_search$', views.basic_search, name='basic_search'),
]