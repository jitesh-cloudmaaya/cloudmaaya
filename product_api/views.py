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
from elasticsearch_dsl.query import Q


from elasticsearch_dsl.connections import connections
from product_doc import EProductSearch#, EProduct


@api_view(['GET'])
def sort_options(self):
    options = EProductSearch.sort_options()

    return Response(options) 



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

    sort_order = self.query_params.get('sort')
    if not sort_order:
        #sort_order = "-allume_score"
        sort_order = "_score"

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


    es = EProductSearch(query=text_query, filters=whitelisted_facet_args, favs=user_favs, sort=sort_order)
    es_count = EProductSearch(query=text_query, filters=whitelisted_facet_args, favs=user_favs, card_count=True)
    es = es[start_record:end_record]
    results = es.execute().to_dict()
    results_count = es_count.execute().to_dict()
    #results_count['aggregations']['unique_count']['value'] = 0
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

    #s = s.query("match_phrase", product_name=product.product_name)[:100]
    
    s.query = Q("match_phrase", product_name=product.product_name) | Q({"ids" : {"values" : product_id}})
    s = s.filter("match_phrase", merchant_name=product.merchant_name)

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

@api_view(['GET'])
@permission_classes((AllowAny, ))
def get_allume_product(self, product_id):
    """

    get:
        Convert product data to allume product data by id
        URL: /product_api/get_allume_product/1570
    """
    product = Product.objects.get(id = product_id)
    p_name = product.product_name

    # using the product we are looking for
    product_merchant_id = product.merchant_id
    # retrieve the merchant from the pam table
    merchant = Merchant.objects.get(external_merchant_id = product_merchant_id)
    # and grab the id used in the internal db representation
    merchant_id = merchant.id

    s = Search(index="products")

    s = s.query("match_phrase", product_name=product.product_name)[0:100]
    s = s.filter("match_phrase", merchant_name=product.merchant_name)

    results = s.execute()

    results_dict = results.to_dict()
    # grab and add _source field dict to add field for API call
    for hit in results_dict['hits']['hits']:
        hit['_source']['product_api_merchant'] = merchant_id

    total_count = s.count()
    page = 1
    facets_dict = {}
    context = format_results(results_dict, total_count, page, 100, self, 'products', p_name, facets_dict)


    results = context


    payload = {'sites': {}}
    tmp = {'color_names': [], 'color_objects': {}}
    matching_object = ''

    data = results['data']
    # loop through results to set up content for the payload
    for i in range(0, len(data)):
        product = data[i]['_source']
        if str(product['id']) == str(product_id) or str(product['product_id']) == str(product_id):
            matching_object = product
        # create color object for payload
        clr = product['merchant_color'].lower()
        if clr not in tmp['color_names']:
            tmp['color_names'].append(clr)
            tmp['color_objects'][clr] = {'sizes': [], 'size_data': {}}

        all_sizes = product['size'].split(',')
        for i in range(0, len(all_sizes)):
            size = all_sizes[i]
            if size not in tmp['color_objects'][clr]['sizes']:
                tmp['color_objects'][clr]['sizes'].append(size)
                size_data = {'image': product['product_image_url'], 'price': product['current_price'], 'text': size, 'value': size} # change formatting?
                tmp['color_objects'][clr]['size_data'][size] = size_data

    # a mapping of the text field, 'availability', to a boolean flag, 'available'
    availability_mapping = {'in-stock': True, '': False, 'out-of-stock': False, 'preorder': False, 'yes': True, 'no': False}
    # either update above as more or fields are added or mold availability field across feeds to the same form

    # create payload object
    merchant_node = str(matching_object['product_api_merchant'])
    product_node = str(product_id)
    payload['sites'][merchant_node] = {}
    payload['sites'][merchant_node]['add_to_cart'] = {}
    payload['sites'][merchant_node]['add_to_cart'][product_node] = {}
    payload['sites'][merchant_node]['add_to_cart'][product_node]['title'] = matching_object['product_name']
    payload['sites'][merchant_node]['add_to_cart'][product_node]['brand'] = matching_object['brand']
    payload['sites'][merchant_node]['add_to_cart'][product_node]['price'] = matching_object['current_price']
    payload['sites'][merchant_node]['add_to_cart'][product_node]['original_price'] = matching_object['retail_price']
    payload['sites'][merchant_node]['add_to_cart'][product_node]['image'] = matching_object['product_image_url']
    payload['sites'][merchant_node]['add_to_cart'][product_node]['description'] = matching_object['long_product_description']
    payload['sites'][merchant_node]['add_to_cart'][product_node]['categories'] = [matching_object['primary_category'], matching_object['secondary_category'], matching_object['allume_category']]
    payload['sites'][merchant_node]['add_to_cart'][product_node]['material'] = matching_object['material']
    payload['sites'][merchant_node]['add_to_cart'][product_node]['is_deleted'] = matching_object['is_deleted']

    try:
        payload['sites'][merchant_node]['add_to_cart'][product_node]['available'] = availability_mapping[matching_object['availability']]
    except KeyError as e:
        print "The 'availablity' text field value present in this product does not have a known mapping, it was assumed to 'available' = False"
        print matching_object['availability']
        payload['sites'][merchant_node]['add_to_cart'][product_node]['available'] = False

    payload['sites'][merchant_node]['add_to_cart'][product_node]['required_field_names'] = ["color", "size", "quantity"]
    payload['sites'][merchant_node]['add_to_cart'][product_node]['required_field_values'] = {}
    payload['sites'][merchant_node]['add_to_cart'][product_node]['required_field_values']['color'] = []
    payload['sites'][merchant_node]['add_to_cart'][product_node]['url'] = matching_object['product_url']
    payload['sites'][merchant_node]['add_to_cart'][product_node]['status'] = "done"
    payload['sites'][merchant_node]['add_to_cart'][product_node]['original_url'] = matching_object['raw_product_url']

    # create the colors array object
    for i in range(0, len(tmp['color_names'])):
        color = tmp['color_names'][i]
        obj = {'dep': {'size': []}, 'price': matching_object['current_price'], 'text': color, 'value': color}
        for j in range(0, len(tmp['color_objects'][color]['sizes'])):
            size_name = tmp['color_objects'][color]['sizes'][j]
            size = tmp['color_objects'][color]['size_data'][size_name]
            size['dep'] = {}
            obj['dep']['size'].append(size)
        payload['sites'][merchant_node]['add_to_cart'][product_node]['required_field_values']['color'].append(obj)

    return Response(payload)

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



