# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework.decorators import (api_view, renderer_classes, permission_classes)
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.renderers import JSONRenderer
from rest_framework_xml.renderers import XMLRenderer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
from elasticsearch_dsl import Search, FacetedSearch, TermsFacet, DateHistogramFacet
from elasticsearch_dsl.aggs import Terms, DateHistogram
from elasticsearch import TransportError
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
import collections
import json
import urllib
import datetime
import urllib
from shopping_tool.models import Look, LookLayout, LookProduct, UserProductFavorite
from models import Product, Merchant


from elasticsearch_dsl.connections import connections
from product_doc import EProductSearch#, EProduct


@api_view(['GET'])
@permission_classes((AllowAny, ))
def facets(self):
    """
    get:
        Get Product Search Results

        /product_api/facets?text=shirts

        Optional Params:
        favs=True : Filters the Search Results for Just User Favorites

        
    """
    text_query = self.query_params.get('text', '*')
    num_per_page = int(self.query_params.get('num_per_page', 100))
    page = int(self.query_params.get('page', 1))

    filter_favs = self.query_params.get('favs')
    if filter_favs:
        user_favs = list(UserProductFavorite.objects.filter(stylist=filter_favs).values_list('product_id', flat=True))
    else:
        user_favs = []
    

    start_record = (num_per_page * (page - 1))
    #print start_record
    end_record = (num_per_page * page) 
    #print end_record

    whitelisted_facet_args = {}
    for key, value in self.query_params.items():
        if key in EProductSearch.facets:
            whitelisted_facet_args[key] = urllib.unquote(value).split("|")


    es = EProductSearch(query=text_query, filters=whitelisted_facet_args, favs=user_favs)
    es_count = EProductSearch(query=text_query, filters=whitelisted_facet_args, favs=user_favs, card_count=True)
    es = es[start_record:end_record]
    results = es.execute().to_dict()
    results_count = es_count.execute().to_dict()
    #results = results_count


    total_count = results_count['aggregations']['unique_count']['value']
    context = format_results(results, total_count, page, num_per_page, self, 'products', text_query, results['aggregations'])


    return Response(context) 


@api_view(['GET'])
@permission_classes((AllowAny, ))
def basic_search(self):

    text_query = self.query_params.get('text', 'shirt')

    s = Search(index="products") \
        .query("match_phrase", product_name=text_query)[0:10]


    facets = ['color', 'manufacturer_name', 'gender', 'size', 'product_type', 'merchant_name']
    for facet in facets:
        s.aggs.bucket(facet, 'terms', field=('%s.keyword' % (facet)))

    response = s.execute()

 

    facets_dict = {}
    for aggregation in response.aggregations:
        print response.aggregations[aggregation].buckets
        facets_dict[aggregation] = response.aggregations[aggregation].buckets

    print facets_dict

    results = s.execute()
    results_dict = results.to_dict()
    results = results_dict['hits']

    page = 1
    total_count = s.count()

    context = format_results(results, total_count, page, 100, self, 'products', text_query, facets_dict)

    return Response(context) 


@api_view(['GET'])
@permission_classes((AllowAny, ))
def get_product(self, product_id):

    product = Product.objects.get(id = product_id)
    p_name = product.product_name

    print product.brand

    # using the product we are looking for
    product_merchant_id = product.merchant_id
    # retrieve the merchant from the pam table
    merchant = Merchant.objects.get(external_merchant_id = product_merchant_id)
    # and grab the id used in the internal db representation
    merchant_id = merchant.id

    s = Search(index="products")

    s = s.query("match_phrase", product_name=product.product_name)[0:100]
    s = s.filter("match_phrase", merchant_name=product.merchant_name)

    #Bool(must=[Terms(brand__keyword=[u'Hudson']), Terms(merchant_name__keyword=[u'Bergdorf Goodman (Neiman Marcus)', u'Lord & Taylor'])]) 



    results = s.execute()


    results_dict = results.to_dict()
    #results = results_dict['hits']
    # grab and add_source field dict to add field for API call
    for hit in results_dict['hits']['hits']:
        hit['_source']['product_api_merchant'] = merchant_id

    total_count = s.count()
    page = 1
    facets_dict = {}

    context = format_results(results_dict, total_count, page, 100, self, 'products', p_name, facets_dict)

    return Response(context) 



def format_results(results, total_count, page, num_per_page, request, label, text_query, facets_dict):
    response = collections.OrderedDict()
    response['request'] = request.get_full_path()
    response['text_query'] = text_query
    response['page'] = page
    response['total_items'] = total_count
    response['total_pages'] = 1
    response['num_per_page'] = num_per_page
    response['object'] = label
    response['facets'] = facets_dict
    response['data'] = results['hits']['hits']
    return response

def convert_facet_value(facet_name, value):
    if facet_name == 'publish_month':
        return value.strftime('%Y-%m')
    return value


def facet_to_filter(facet_name, value):
    if facet_name == 'publish_month':
        yyyy, mm = map(int, value.split('-'))
        return datetime.datetime(yyyy, mm, 1, 0, 0, 0)
    return value

def href_with_removed(key, value, query_params):
    existing = dict(query_params)
    for key, value in existing.items():
        existing[key] = value.encode('utf8')
    if key in existing:
        del existing[key]
    return '/?' + urllib.urlencode(existing)


def href_with_added(key, value, query_params):
    existing = dict(query_params)
    existing[key] = value
    for key, value in existing.items():
        existing[key] = value.encode('utf8')
    return '/?' + urllib.urlencode(existing)



