from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^set_cookie/$', views.set_cookie, name='set_cookie'),
    url(r'^delete_cookie/$', views.delete_cookie, name='delete_cookie'),
    url(r'^add_product_to_rack/$', views.add_product_to_rack, name='add_product_to_rack'),   
]