from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'final_sale_check/(?P<allume_cart_id>\d+)/$', views.final_sale_check, name='final_sale_check'),
    url(r'proxy/$', views.proxy, name='proxy'),
    url(r'submit_final_sale_check/$', views.submit_final_sale_check, name='submit_final_sale_check'),
    url(r'get_unchecked_final_sale_data/$', views.get_unchecked_final_sale_data, name='get_unchecked_final_sale_data'),
]