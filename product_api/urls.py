from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^basic_search$', views.basic_search, name='basic_search'),
    url(r'^facets$', views.facets, name='facets'),
    url(r'^get_product/(?P<product_id>[0-9]+)/$', views.get_product, name='get_product'),
    url(r'^get_allume_product/(?P<product_id>[0-9]+)/$', views.get_allume_product, name='get_allume_product')
]
