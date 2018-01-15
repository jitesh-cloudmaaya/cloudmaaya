from django.conf.urls import url



from . import views

urlpatterns = [
    url(r'^(?P<styling_session_id>[0-9]+)/$', views.index, name='index'),
    url(r'^explore_looks/(?P<styling_session_id>[0-9]+)/$', views.explore, name='explore'),
    url(r'^set_cookie/$', views.set_cookie, name='set_cookie'),
    url(r'^delete_cookie/$', views.delete_cookie, name='delete_cookie'),
    url(r'^image_proxy/$', views.image_proxy, name='image_proxy'),
    url(r'^collage/(?P<look_id>[0-9]+)/$', views.collage, name='collage'),
]