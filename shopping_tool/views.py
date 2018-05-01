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
from product_api.models import Product, MerchantCategory, AllumeCategory

from shopping_tool_api.serializers import *
from rest_framework.renderers import JSONRenderer

import requests
from PIL import Image
from catalogue_service.settings_local import PRODUCT_IMAGE_PROXY
from catalogue_service.settings_local import AUTH_LOGIN_URL, AUTH_EMAIL_KEY, DEV_AUTH_EMAIL
from catalogue_service.settings_local import IMGKIT_URL, IMGKIT_OPTIONS
from catalogue_service.settings_local import ENV_LOCAL

from weather_service.models import Weather
import imgkit


# Create your views here. 

def category_samples(request):
    cat1 = request.GET['external_cat1']
    cat2 = request.GET['external_cat2']

    print cat1
    print cat2
    
    products = Product.objects.filter(primary_category = cat1).filter(secondary_category = cat2)
    products = products.filter(is_deleted = 0)
    products = products.all()[:20]
    for product in products:
        print product

    context = {'products': products, 'cat1': cat1, 'cat2': cat2}

    return render(request, 'shopping_tool/category_samples.html', context) 


@check_login
def index(request, styling_session_id=None):

    user = request.user
    layouts = LookLayout.objects.all()
    
    try:
        styling_session = AllumeStylingSessions.objects.get(id = styling_session_id) 
    except AllumeStylingSessions.DoesNotExist:
        context = {}
        return render(request, 'shopping_tool/no_session_error.html', context)

    rack_items = Rack.objects.filter(stylist = user.id).filter(allume_styling_session = styling_session)
    looks = Look.objects.filter(allume_styling_session = styling_session)
    client = styling_session.client
    weather_info = Weather.objects.retrieve_weather_object(city=client.client_360.where_live_city, state=client.client_360.where_live_state)
    categories = AllumeCategory.objects.filter(active = True).order_by('position')
    favorites = UserProductFavorite.objects.filter(stylist = user.id)
    styles = StyleType.objects.filter(active=True).all()
    occasions = StyleOccasion.objects.filter(active=True).all()    
    product_image_proxy = PRODUCT_IMAGE_PROXY
    env = ENV_LOCAL

    context = {'product_image_proxy': product_image_proxy, 'favorites': favorites, 
               'categories': categories, 'user': user, 'styling_session': styling_session, 
               'rack_items': rack_items, 'client': client, 'layouts': layouts,
               'looks': looks, 'weather_info': weather_info,'styles': styles,
               'occasions': occasions, 'env': env}
               
    return render(request, 'shopping_tool/index.html', context)


@check_login
def look_builder(request, styling_session_id=None):

    user = request.user
    layouts = LookLayout.objects.all()
    
    try:
        styling_session = AllumeStylingSessions.objects.get(id = styling_session_id) 
    except AllumeStylingSessions.DoesNotExist:
        context = {}
        return render(request, 'shopping_tool/no_session_error.html', context)

    rack_items = Rack.objects.filter(stylist = user.id).filter(allume_styling_session = styling_session)
    looks = Look.objects.filter(allume_styling_session = styling_session)
    client = styling_session.client
    weather_info = Weather.objects.retrieve_weather_object(city=client.client_360.where_live_city, state=client.client_360.where_live_state)
    categories = AllumeCategory.objects.filter(active = True)
    favorites = UserProductFavorite.objects.filter(stylist = user.id)
    styles = StyleType.objects.filter(active=True).all()
    occasions = StyleOccasion.objects.filter(active=True).all()
    product_image_proxy = PRODUCT_IMAGE_PROXY
    env = ENV_LOCAL

    context = {'product_image_proxy': product_image_proxy, 'favorites': favorites, 
               'categories': categories, 'user': user, 'styling_session': styling_session, 
               'rack_items': rack_items, 'client': client, 'layouts': layouts,
               'looks': looks, 'weather_info': weather_info, 'styles': styles,
               'occasions': occasions, 'env': env}
               
    return render(request, 'shopping_tool/look_builder.html', context)



#@check_login
def collage(request, look_id=None):
    try:
        look = Look.objects.get(id = look_id) 
    except Look.DoesNotExist:
        context = {}
        return render(request, 'shopping_tool/no_look.html', context)

    serializer = LookSerializer(look)
    json = JSONRenderer().render(serializer.data)
    product_image_proxy = PRODUCT_IMAGE_PROXY

    context = { 'look': look, 'look_json': json, 'product_image_proxy': product_image_proxy }

    return render(request, 'shopping_tool/collage.html', context)


# https://github.com/jarrekk/imgkit
# http://madalgo.au.dk/~jakobt/wkhtmltoxdoc/wkhtmltoimage_0.10.0_rc2-doc.html
def collage_image(request, look_id=None):

    try:
        look = Look.objects.get(id = look_id) 
        img_src = imgkit.from_url('%s/collage/%s' % (IMGKIT_URL, look_id), False, options = IMGKIT_OPTIONS)
        response = HttpResponse(img_src, content_type="image/jpeg")
        response['Cache-Control'] = 'max-age=0'
        return response
    except Look.DoesNotExist:
        return HttpResponse(status=404)

@check_login
def explore(request, styling_session_id=None):

    user = request.user
    layouts = LookLayout.objects.all()

    try:
        styling_session = AllumeStylingSessions.objects.get(id = styling_session_id) 
    except AllumeStylingSessions.DoesNotExist:
        context = {}
        return render(request, 'shopping_tool/no_session_error.html', context)

    rack_items = Rack.objects.filter(stylist = user.id).filter(allume_styling_session = styling_session)
    looks = Look.objects.filter(allume_styling_session = styling_session)
    client = styling_session.client
    weather_info = Weather.objects.retrieve_weather_object(city=client.client_360.where_live_city, state=client.client_360.where_live_state)
    stylists = WpUsers.objects.stylists()
    favorites = UserProductFavorite.objects.filter(stylist = user.id)
    styles = StyleType.objects.filter(active=True).all()
    occasions = StyleOccasion.objects.filter(active=True).all()    
    product_image_proxy = PRODUCT_IMAGE_PROXY
    env = ENV_LOCAL

    context = {'favorites': favorites, 'user': user, 'stylists': stylists, 
               'styling_session': styling_session, 'rack_items': rack_items, 
               'client': client, 'layouts': layouts, 'looks': looks,
               'product_image_proxy': product_image_proxy, 'styles': styles,
               'occasions': occasions, 'weather_info': weather_info, 'env': env}

    return render(request, 'shopping_tool/explore.html', context)


########################################################
# localdev Only Method to support Image Proxy in order
# to support cropping
########################################################

def image_proxy(request):
    
    url = request.GET.get('image_url')
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    image_data = requests.get(url, headers=headers, stream=True)
    image_data.raw.decode_content = True
    im = Image.open(image_data.raw)
    response = HttpResponse(content_type="image/png")
    im.save(response, "PNG")

    return response

########################################################
# Some Localdev Methods In Order to Test Login
# without Having Access to The WP Login Application
########################################################
def set_cookie(request):
    if request.get_host() in ['localhost:8000', '127.0.0.1:8000', 'shopping-tool-web-dev.allume.co:8000']:
        response_redirect = HttpResponseRedirect('/')
        response_redirect.set_cookie(AUTH_EMAIL_KEY, DEV_AUTH_EMAIL)
        return response_redirect
    else:
        raise PermissionDenied

def delete_cookie(request):
    if request.get_host() in ['localhost:8000', '127.0.0.1:8000', 'shopping-tool-web-dev.allume.co:8000']:
        response_redirect = HttpResponseRedirect('/')
        response_redirect.delete_cookie(AUTH_EMAIL_KEY)
        return response_redirect
    else:
        raise PermissionDenied