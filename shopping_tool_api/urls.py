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
    url(r'^client_360/(?P<pk>[0-9]+)/$', views.client_360, name='client_360'),
    url(r'^styling_session_note/(?P<pk>[0-9]+)/$', views.styling_session_note, name='styling_session_note'),
    url(r'^styling_session_notes/(?P<pk>[0-9]+)/$', views.styling_session_notes, name='styling_session_notes'),
    url(r'^look_meta_tags/(?P<pk>[0-9]+)/$', views.look_meta_tags, name='look_meta_tags'),
    url(r'^style_occasions/$', views.style_occasions, name='style_occasions'),  
    url(r'^style_type/$', views.style_type, name='style_type'),  
    url(r'^update_look_position/(?P<pk>[0-9]+)/$', views.update_look_position, name='update_look_position'),

]

