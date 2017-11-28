from django.conf.urls import url


from . import views

urlpatterns = [
    url(r'^layouts/$', views.layouts, name='layouts'),   
    url(r'^look/(?P<pk>[0-9]+)/$', views.look, name='look'), 
    url(r'^rack_item/(?P<pk>[0-9]+)/$', views.rack_item, name='rack_item'), 
    url(r'^rack_item/$', views.rack_item, name='rack_item'), 
    url(r'^product_look/(?P<pk>[0-9]+)/$', views.product_look, name='product_look'),     
]