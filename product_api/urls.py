from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^basic_search$', views.basic_search, name='basic_search'),
    url(r'^facets$', views.facets, name='facets'),
    url(r'^get_product/(?P<product_id>[0-9]+)/(?P<final_sale>[0-1])/$', views.get_product, name='get_product'),
    url(r'^set_product_final_sale/(?P<product_id>[0-9]+)/$', views.set_product_final_sale, name='set_product_final_sale'),
    url(r'^get_allume_product/(?P<product_id>[0-9]+)/$', views.get_allume_product, name='get_allume_product'),
    url(r'^get_allume_products/$', views.get_allume_products, name='get_allume_products'),
    url(r'^sort_options$', views.sort_options, name='sort_options'),

]
