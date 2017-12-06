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
from rest_framework.parsers import JSONParser
from rest_framework_xml.renderers import XMLRenderer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
from shopping_tool.decorators import check_login
from django.core.exceptions import PermissionDenied
from product_api.models import Product
from shopping_tool.models import AllumeClients, Rack, AllumeStylingSessions, AllumeStylistAssignments
from shopping_tool.models import Look, LookLayout, LookProduct, UserProductFavorite
from serializers import RackSerializer, RackCreateSerializer, LookCreateSerializer, LookProductSerializer
from serializers import UserProductFavoriteSerializer, LookProductCreateSerializer, LookSerializer, UserProductFavoriteDetailSerializer
from rest_framework import status



@api_view(['GET', 'PUT', 'DELETE'])
@check_login
@permission_classes((AllowAny, ))
def user_product_favorite(request, pk=None):
    """
    get:
        View user favorite product ID

        /shopping_tool_api/user_favorites/{favorite_id}/
    put:
        Add product to the user favorites

        /shopping_tool_api/user_favorites/0/

        Sample JSON Object

        {
          "stylist": 1,
          "product": 393223
        }

    delete:
        Remove a product from the rack for a styling session
        
    """
    if request.method == 'GET':
        try:
            fav = UserProductFavorite.objects.get(id=pk)
        except UserProductFavorite.DoesNotExist:
            return HttpResponse(status=404)

        serializer = UserProductFavoriteDetailSerializer(fav)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'PUT':
        serializer = UserProductFavoriteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        try:
            fav = UserProductFavorite.objects.get(id = pk)
            fav.delete()
            context = {'Success': True}
            return JsonResponse(context, status=status.HTTP_201_CREATED)
        except ObjectDoesNotExist as er:
            context = {'Success': False, 'Info': str(er)}
            return JsonResponse(context, status=status.HTTP_400_BAD_REQUEST)

        return Response(context) 


@api_view(['GET'])
@check_login
@permission_classes((AllowAny, ))
def user_product_favorites(request, pk=None):
    """
    get:
        View list of user favorite product IDs

        /shopping_tool_api/user_favorites/{userid}/

    """
    try:
        favs = UserProductFavorite.objects.filter(stylist=pk).all()
    except UserProductFavorite.DoesNotExist:
        return HttpResponse(status=404)

    serializer = UserProductFavoriteSerializer(favs, many=True)
    return JsonResponse(serializer.data, safe=False)


@api_view(['GET', 'PUT', 'DELETE'])
@check_login
@permission_classes((AllowAny, ))
def rack_item(request, pk=None):
    """
    get:
        View product from the rack for a styling session by rack id
    put:
        Add product to the rack for a styling session

        /shopping_tool_api/rack_item/0/

        Sample JSON Object

        {
          "product": 393223,
          "allume_styling_session": 3
        }

    delete:
        Remove a product from the rack for a styling session
    """
    if request.method == 'GET':
        try:
            rack_item = Rack.objects.get(id=pk)
        except Rack.DoesNotExist:
            return HttpResponse(status=404)

        serializer = RackSerializer(rack_item)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'PUT':
        serializer = RackCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        try:
            rack_item = Rack.objects.get(id = pk)
            rack_item.delete()
            context = {'Success': True}
            return JsonResponse(context, status=status.HTTP_201_CREATED)
        except ObjectDoesNotExist as er:
            context = {'Success': False, 'Info': str(er)}
            return JsonResponse(context, status=status.HTTP_400_BAD_REQUEST)


        return Response(context) 


@api_view(['GET', 'PUT'])
@check_login
@permission_classes((AllowAny, ))
def look(request, pk):
    """
    get:
        Get a look and its products, layouts, etc
    put:
        Create or update a look

        Sample JSON Create Object
        URL: /shopping_tool_api/look/0/

        {
         "name": "Test Look 5huck",
         "look_layout": 1,
         "allume_styling_session":3,
         "stylist": 117
        }
    """



    if request.method == 'GET':

        try:
            look = Look.objects.get(id=pk)
        except Look.DoesNotExist:
            return HttpResponse(status=404)

        serializer = LookSerializer(look)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'PUT':

        try:
            look = Look.objects.get(id=pk)
            serializer = LookSerializer(look, data=request.data)
        except Look.DoesNotExist:
            serializer = LookCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)


@api_view(['POST'])
@check_login
@permission_classes((AllowAny, ))
def look_list(request):
    """
    post:
        Get a list of looks filtered by shopper, client or styling_session and its products, layouts, etc
       
        Sample JSON Object, all filters below are optional.
        {
         "client": 1,
         "allume_styling_session":3,
         "stylist": 117,
         "name": "Body Suit"
        }
    """
    looks = Look.objects.all()

    if 'client' in request.data:
        client = request.data['client']
        styling_sessions = AllumeStylingSessions.objects.filter(client = client).values_list('id', flat=True)
        looks = looks.filter(allume_styling_session__in = styling_sessions)

    if 'allume_styling_session' in request.data:
        allume_styling_session = request.data['allume_styling_session']
        looks = looks.filter(allume_styling_session = allume_styling_session)

    if 'stylist' in request.data:
        stylist = request.data['stylist']
        looks = looks.filter(stylist = stylist)

    if 'name' in request.data:
        name = request.data['name']
        looks = looks.filter(name__contains = name)

    serializer = LookSerializer(looks, many=True)
    return JsonResponse(serializer.data, safe=False)
   

@api_view(['GET', 'PUT', 'DELETE'])
@check_login
@permission_classes((AllowAny, ))
def look_item(request, pk=None):
    """
    get:
        View product from a look for a styling session by look id
    put:
        Add or Update product to a look for a styling session

        Sample JSON Create Object
        URL: /shopping_tool_api/look_item/0/

        {
          "layout_position": 4,
          "look": 5,
          "product": 393223
        }


        Sample JSON Update Object
        URL: /shopping_tool_api/look_item/2/

        {
          "id": 2,
          "layout_position": 4,
          "look": 5,
          "product": 393223
        }

    delete:
        Remove a product from a look for a styling session
    """
    if request.method == 'GET':
        try:
            look_item = LookProduct.objects.get(id=pk)
        except LookProduct.DoesNotExist:
            return HttpResponse(status=404)

        serializer = LookProductSerializer(look_item)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'PUT':

        try:
            look_item = LookProduct.objects.get(id=pk)
            serializer = LookProductCreateSerializer(look_item, data=request.data)
        except LookProduct.DoesNotExist:
            serializer = LookProductCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)

        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        try:
            look_item = LookProduct.objects.get(id = pk)
            look_item.delete()
            context = {'Success': True}
            return JsonResponse(context, status=status.HTTP_201_CREATED)
        except ObjectDoesNotExist as er:
            context = {'Success': False, 'Info': str(er)}
            return JsonResponse(context, status=status.HTTP_400_BAD_REQUEST)

        return Response(context) 


@api_view(['GET'])
@check_login
@permission_classes((AllowAny, ))
def layouts(request):
    """
    get:
        List of available look layouts
    """
    layouts = LookLayout.objects.values()
    return Response(layouts) 
