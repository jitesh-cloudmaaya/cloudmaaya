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
import collections
import json
from elasticsearch import TransportError
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

# Create your views here.




class FSearch(FacetedSearch):
    #doc_types = ['Article']
    # fields that should be searched
    #client = Elasticsearch()
    fields = ['product_name']
    #using = client
    #['short_product_description','long_product_description', 'product_name', 'color']
    #index = "logstash-*"
    facets = {
        'manufacturer_name': TermsFacet(field='manufacturer_name.keyword'),
        'color': TermsFacet(field='color.keyword')
    }



    #def search(self):
    #    # override methods to add custom pieces
    #    s = super().search()
    #    return s#.filter('range', publish_from={'lte': 'now/h'})


@api_view(['GET'])
def facets(self):
    bs = FSearch('shoes')
    print bs.count()
    #', {'publishing_frequency': date(2015, 6)})
    response = bs.execute()
    print bs.count()

    # access hits and other attributes as usual
    print(response.hits.total, 'hits total')
    for hit in response:
        print(hit.meta.score, hit.product_name)

    for (manufacturer_name, count, selected) in response.facets.manufacturer_name:
        print(manufacturer_name, ' (SELECTED):' if selected else ':', count)

    return Response(response.hits) 



@api_view(['GET'])
def basic_search(self):

    text_query = self.query_params.get('text', 'shirt')

    s = Search(index="logstash-*") \
        .query("match_phrase", product_name=text_query)[0:10]

    s.aggs.bucket('per_tag', 'terms', field='manufacturer_name.keyword')

    response = s.execute()

    for tag in response.aggregations.per_tag.buckets:
        print(tag.key, tag.doc_count)    

    results = s.execute()
    results_dict = results.to_dict()
    results = results_dict['hits']

    page = 1
    total_count = s.count()

    context = format_results(results, total_count, page, self, 'products', text_query)

    return Response(context) 





def format_results(results, total_count, page, request, label, text_query):
    response = collections.OrderedDict()
    response['request'] = request.get_full_path()
    response['text_query'] = text_query
    response['page'] = page
    response['total_items'] = total_count
    response['total_pages'] = 1
    response['num_per_page'] = len(results['hits'])
    response['object'] = label
    response['data'] = results['hits']
    return response




