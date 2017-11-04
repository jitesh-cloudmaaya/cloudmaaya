# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from rest_framework.decorators import (api_view, renderer_classes)
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.renderers import JSONRenderer
from rest_framework_xml.renderers import XMLRenderer
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

from elasticsearch_dsl.connections import connections
from product_doc import EProductSearch#, EProduct


@api_view(['GET'])
def facets(self):

    text_query = self.query_params.get('text', 'shirt')


    es = EProductSearch(query=text_query, filters={})
    es = es[:20]
    response = es.execute()

    facets = response.facets
    # Hack to order them by the order defined in EmailSearch.facets
    facets = [(key, value) for key, value in facets._d_.items()]
    facets.sort(key=lambda p: EProductSearch.facets.keys().index(p[0]))
    facet_dicts = []
    for facet_name, values in facets:
        facet_values = []
        for value, count, selected in values:
            value = convert_facet_value(facet_name, value)
            if selected:
                href = href_with_removed(facet_name, value)
            else:
                href = href_with_added(facet_name, value)
            facet_values.append({
                'value': value,
                'count': count,
                'selected': selected,
                'href': href,
            })
        d = {
            'name': facet_name,
            'vals': facet_values,
        }
        facet_dicts.append(d)

    print facet_dicts

    return Response(response.to_dict()) 


@api_view(['GET'])
def basic_search(self):

    text_query = self.query_params.get('text', 'shirt')

    s = Search(index="logstash-*") \
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

    context = format_results(results, total_count, page, self, 'products', text_query, facets_dict)

    return Response(context) 





def format_results(results, total_count, page, request, label, text_query, facets_dict):
    response = collections.OrderedDict()
    response['request'] = request.get_full_path()
    response['text_query'] = text_query
    response['page'] = page
    response['total_items'] = total_count
    response['total_pages'] = 1
    response['num_per_page'] = len(results['hits'])
    response['object'] = label
    response['facets'] = facets_dict
    response['data'] = results['hits']
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

def href_with_removed(key, value):
    #existing = dict(request.args.iteritems())
    #for key, value in existing.items():
    #    existing[key] = value.encode('utf8')
    #if key in existing:
    #    del existing[key]
    #return '/?' + urllib.urlencode(existing)
    return key


def href_with_added(key, value):
    #existing = dict(request.args.iteritems())
    #existing[key] = value
    #for key, value in existing.items():
    #    existing[key] = value.encode('utf8')
    #return '/?' + urllib.urlencode(existing)
    return key


