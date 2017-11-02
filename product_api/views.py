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
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, FacetedSearch, TermsFacet, DateHistogramFacet
import json

# Create your views here.


client = Elasticsearch()

@api_view(['GET'])
def basic_search(self):
	text_query = self.query_params.get('text', None)

	s = Search(using=client, index="products") \
	    .query("match", product_name=text_query)[0:50]   \

	s[0:50]
	results = s.execute()
	results_dict = results.to_dict()
	print results_dict['hits']
	results = results_dict['hits']

	page = 1
	total_count = s.count()

	context = format_results(results, total_count, page, self, 'products')

	return Response(context) 


def format_results(results, total_count, page, request, label):
    response = {}
    response['request'] = request.get_full_path()
    response['page'] = page
    response['total_items'] = total_count
    response['total_pages'] = 1
    response['num_per_page'] = len(results['hits'])
    response['object'] = label
    response['data'] = results['hits']
    return response