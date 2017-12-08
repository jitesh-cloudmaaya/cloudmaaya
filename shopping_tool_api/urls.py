from django.conf.urls import url


from . import views

urlpatterns = [
    url(r'^layouts/$', views.layouts, name='layouts'),   
    url(r'^look/(?P<pk>[0-9]+)/$', views.look, name='look'), 
    url(r'^rack_item/(?P<pk>[0-9]+)/$', views.rack_item, name='rack_item'), 
    url(r'^look_item/(?P<pk>[0-9]+)/$', views.look_item, name='look_item'), 
    url(r'^look_list/$', views.look_list, name='look_list'),  
    url(r'^user_product_favorites/(?P<pk>[0-9]+)/$', views.user_product_favorites, name='user_product_favorites'),  
    url(r'^user_product_favorite/(?P<pk>[0-9]+)/$', views.user_product_favorite, name='user_product_favorite'),
    url(r'^user_look_favorites/(?P<pk>[0-9]+)/$', views.user_look_favorites, name='user_look_favorites'),  
    url(r'^user_look_favorite/(?P<pk>[0-9]+)/$', views.user_look_favorite, name='user_look_favorite'),
]

