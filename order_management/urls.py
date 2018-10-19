from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'final_sale_check/(?P<allume_cart_id>\d+)/$', views.final_sale_check, name='final_sale_check'),
    url(r'proxy/$', views.proxy, name='proxy'),
]