# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render
from django.db import DatabaseError, IntegrityError
from django.core.exceptions import ObjectDoesNotExist
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
from .models import AllumeClients, Rack, AllumeStylingSessions, AllumeStylistAssignments, Look, LookLayout, WpUsers, UserProductFavorite
from product_api.models import Product, MerchantCategory

import requests
from PIL import Image
from catalogue_service.settings_local import PRODUCT_IMAGE_PROXY


from weather_service.models import Weather

# Create your views here. 

@check_login
def index(request, styling_session_id=None):

    user = request.user
    layouts = LookLayout.objects.values()
    
    try:
        styling_session = AllumeStylingSessions.objects.get(id = styling_session_id) 
    except AllumeStylingSessions.DoesNotExist:
        context = {}
        return render(request, 'shopping_tool/no_session_error.html', context)

    rack_items = Rack.objects.filter(allume_styling_session = styling_session)
    looks = Look.objects.filter(allume_styling_session = styling_session)
    client = styling_session.client
    weather_info = Weather.objects.retrieve_weather_object(city=client.client_360.where_live_city, state=client.client_360.where_live_state)
    categories = MerchantCategory.objects.filter(active = True)
    favorites = UserProductFavorite.objects.filter(stylist = user.id)
    product_image_proxy = PRODUCT_IMAGE_PROXY

    context = {'product_image_proxy': product_image_proxy, 'favorites': favorites, 
               'categories': categories, 'user': user, 'styling_session': styling_session, 
               'rack_items': rack_items, 'client': client, 'layouts': layouts,
               'looks': looks, 'weather_info': weather_info}
               
    return render(request, 'shopping_tool/index.html', context)


@check_login
def explore(request, styling_session_id=None):

    user = request.user
    layouts = LookLayout.objects.values()

    try:
        styling_session = AllumeStylingSessions.objects.get(id = styling_session_id) 
    except AllumeStylingSessions.DoesNotExist:
        context = {}
        return render(request, 'shopping_tool/no_session_error.html', context)

    rack_items = Rack.objects.filter(allume_styling_session = styling_session)
    looks = Look.objects.filter(allume_styling_session = styling_session)
    client = styling_session.client
    weather_info = Weather.objects.retrieve_weather_object(city=client.client_360.where_live_city, state=client.client_360.where_live_state)
    stylists = WpUsers.objects.stylists()
    favorites = UserProductFavorite.objects.filter(stylist = user.id)
    product_image_proxy = PRODUCT_IMAGE_PROXY

    context = {'favorites': favorites, 'user': user, 'stylists': stylists, 
               'styling_session': styling_session, 'rack_items': rack_items, 
               'client': client, 'layouts': layouts, 'looks': looks,
               'product_image_proxy': product_image_proxy, 'weather_info': weather_info}

    return render(request, 'shopping_tool/explore.html', context)


########################################################
# localdev Only Method to support Image Proxy in order
# to support cropping
########################################################

def image_proxy(request):
    
    url = request.GET.get('image_url')

    im = Image.open(requests.get(url, stream=True).raw)
    response = HttpResponse(content_type="image/png")
    im.save(response, "PNG")

    return response

########################################################
# Some Localdev Methods In Order to Test Login
# without Having Access to The WP Login Application
########################################################
def set_cookie(request):
    if request.get_host() in ['localhost:8000', '127.0.0.1:8000', 'shopping-tool-stage.allume.co']:
        response_redirect = HttpResponseRedirect('/')
        #response_redirect.set_cookie('user_email', '1a80b36b569b69579b25ad4583b5c841allume.co')
        response_redirect.set_cookie('user_email', '5bebaefa812e3ca46e70217a994c895fallume.co')
        #response_redirect.set_cookie('user_email', '3ab84d49688d3dd2c947cfce43194d54llume.co')
        return response_redirect
    else:
        raise PermissionDenied

def delete_cookie(request):
    if request.get_host() in ['localhost:8000', '127.0.0.1:8000', 'shopping-tool-stage.allume.co']:
        response_redirect = HttpResponseRedirect('/')
        response_redirect.delete_cookie('user_email')
        return response_redirect
    else:
        raise PermissionDenied