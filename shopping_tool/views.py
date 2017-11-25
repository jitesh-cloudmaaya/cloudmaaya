# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.db import DatabaseError, IntegrityError
from django.template.context_processors import csrf
from rest_framework.decorators import (api_view, renderer_classes, permission_classes)
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.renderers import JSONRenderer
from rest_framework_xml.renderers import XMLRenderer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
from decorators import check_login
from django.core.exceptions import PermissionDenied
from .models import AllumeClients, Rack, AllumeStylingSessions, AllumeStylistAssignments, Look, LookLayout
from product_api.models import Product

# Create your views here.

@check_login
def index(request):

    user = request.user
    styling_session = AllumeStylingSessions.objects.get(id = 3)
    rack_items = Rack.objects.filter(allume_styling_session = styling_session)
    client = styling_session.client

    context = {'user': user, 'styling_session': styling_session, 'rack_items': rack_items, 'client': client}
    return render(request, 'shopping_tool/index.html', context)


@api_view(['GET'])
@check_login
@permission_classes((AllowAny, ))
def add_product_to_rack(request):

    product_id = request.query_params.get('product_id')
    product = Product.objects.get(id = product_id)

    allume_styling_session_id = int(request.query_params.get('allume_styling_session_id'))
    allume_styling_session = AllumeStylingSessions.objects.get(id = allume_styling_session_id)

    user = request.user

    try:
        add_product = Rack.objects.create(product = product, allume_styling_session = allume_styling_session)
        context = {'Success': True, 'Product_Rack_ID': add_product.id}
    except IntegrityError as er:
        context = {'Success': False, 'Info': str(er)}

    return Response(context) 

@api_view(['GET'])
@check_login
@permission_classes((AllowAny, ))
def create_look(request):


    allume_styling_session_id = int(request.query_params.get('allume_styling_session_id'))
    allume_styling_session = AllumeStylingSessions.objects.get(id = allume_styling_session_id)
    look_layout_id = int(request.query_params.get('look_layout_id'))
    look_name = request.query_params.get('look_name')

    look_layout = LookLayout.objects.get(id = look_layout_id)

    stylist = request.user

    try:
        create_look = Look.objects.create(stylist = stylist, allume_styling_session = allume_styling_session, look_layout = look_layout, name = look_name)
        context = {'Success': True, 'Look_ID': create_look.id}
    except IntegrityError as er:
        context = {'Success': False, 'Info': str(er)}

    return Response(context) 



@api_view(['GET'])
@check_login
@permission_classes((AllowAny, ))
def get_layouts(request):

    layouts = LookLayout.objects.values()
    return Response(layouts) 




"""
@api_view(['GET'])
@check_login
@permission_classes((AllowAny, ))
def add_product_to_look(request):

    product_id = request.query_params.get('product_id')
    product = Product.objects.get(id = product_id)
    look = Look.objects.get(id = product_id)

    allume_styling_session_id = int(request.query_params.get('allume_styling_session_id'))
    allume_styling_session = AllumeStylingSessions.objects.get(id = allume_styling_session_id)

    user = request.user

    try:
        add_product = Rack.objects.create(product = product, allume_styling_session = allume_styling_session)
        context = {'Success': True, 'Look_ID': create_look.id}
    else:
        context = "Error"

    return Response(context) 
"""

########################################################
# Some Localdev Methods In Order to Test Login
# without Having Access to The WP Login Application
########################################################
def set_cookie(request):
    if request.get_host() in ['localhost:8000', '127.0.0.1:8000']:
        response_redirect = HttpResponseRedirect('/')
        response_redirect.set_cookie('user_email', 'aaron+test1@allume.co')
        return response_redirect
    else:
        raise PermissionDenied

def delete_cookie(request):
    if request.get_host() in ['localhost:8000', '127.0.0.1:8000']:
        response_redirect = HttpResponseRedirect('/')
        response_redirect.delete_cookie('user_email')
        return response_redirect
    else:
        raise PermissionDenied