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
from shopping_tool.models import Look, LookLayout, LookProduct, UserProductFavorite, UserLookFavorite, AllumeClient360
from serializers import *
from rest_framework import status
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

@api_view(['GET', 'PUT', 'DELETE'])
@check_login
@permission_classes((AllowAny, ))
def client_360(request, pk=None):
    """
    get:
        View client 360

        /shopping_tool_api/client_360/{client_id}/      
    """
    try:
        client = AllumeClient360.objects.get(id=pk)
    except AllumeClient360.DoesNotExist:
        return HttpResponse(status=404)

    serializer = AllumeClient360Serializer(client)
    return JsonResponse(serializer.data, safe=client)

@api_view(['GET', 'PUT', 'DELETE'])
@check_login
@permission_classes((AllowAny, ))
def user_look_favorite(request, pk=None):
    """
    get:
        View user favorite look ID

        /shopping_tool_api/user_look_favorites/{favorite_id}/
    put:
        Add look to the user favorites

        /shopping_tool_api/user_look_favorites/0/

        Sample JSON Object

        {
          "stylist": 1,
          "look": 393223
        }

    delete:
        Remove a product from the rack for a styling session        
    """
    if request.method == 'GET':
        try:
            fav = UserLookFavorite.objects.get(id=pk)
        except UserLookFavorite.DoesNotExist:
            return HttpResponse(status=404)

        serializer = UserLookFavoriteDetailSerializer(fav)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'PUT':
        serializer = UserLookFavoriteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        try:
            fav = UserLookFavorite.objects.get(id = pk)
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
def user_look_favorites(request, pk=None):
    """
    get:
        View list of user favorite looks

        /shopping_tool_api/user_look_favorites/{userid}/
    """
    try:
        favs = UserLookFavorite.objects.filter(stylist=pk).all()
    except UserLookFavorite.DoesNotExist:
        return HttpResponse(status=404)

    serializer = UserLookFavoriteSerializer(favs, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(['GET', 'PUT', 'DELETE'])
@check_login
@permission_classes((AllowAny, ))
def user_product_favorite(request, pk=None):
    """
    get:
        View user favorite product ID

        /shopping_tool_api/user_product_favorite/{favorite_id}/
    put:
        Add product to the user user_product_favorite

        /shopping_tool_api/user_product_favorite/0/

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

        /shopping_tool_api/user_product_favorites/{userid}/
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
         "stylist": 117,
         "description": ""
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
         "name": "Body Suit",
         "page": 1,
         "per_page": 20,
         "favorites_only": True
        }
    """
    looks = Look.objects.all()#filter(look_layout > None)

    page = 1
    if 'page' in request.data:
        page = request.data['page']

    per_page = 20
    if 'per_page' in request.data:
        per_page = request.data['per_page']

    if 'client' in request.data:
        client = request.data['client']
        styling_sessions = AllumeStylingSessions.objects.filter(client = client).values_list('id', flat=True)
        looks = looks.filter(allume_styling_session__in = styling_sessions)

    if 'allume_styling_session' in request.data:
        allume_styling_session = request.data['allume_styling_session']
        looks = looks.filter(allume_styling_session = allume_styling_session)

    if 'stylist' in request.data:
        stylist = request.data['stylist']
        print stylist
        looks = looks.filter(stylist = stylist)

        print looks.count()

    if 'name' in request.data:
        name = request.data['name']
        looks = looks.filter(Q(name__icontains = name) | Q(description__icontains = name))

    if 'favorites_only' in request.data:
        if request.data['favorites_only'] == "True":
            favs = UserLookFavorite.objects.filter(stylist=request.user.id).values_list('look_id', flat=True)
            looks = looks.filter(id__in = favs)


    lookmetrics = LookMetrics.objects.all()

    if 'total_look_price' and 'total_look_price_comparison' in request.data:
        comparison = request.data['total_look_price_comparison']
        threshold = request.data['total_look_price']
        if comparison == 'lt':
            lookmetrics = LookMetrics.objects.filter(total_look_price__lt = threshold)
        elif comparison == 'lte':
            lookmetrics = LookMetrics.objects.filter(total_look_price__lte = threshold)
        elif comparison == 'e':
            lookmetrics = LookMetrics.objects.filter(total_look_price = threshold)
        elif comparison == 'gte':
            lookmetrics = LookMetrics.objects.filter(total_look_price__gte = threshold)
        elif comparison == 'gt':
            lookmetrics = LookMetrics.objects.filter(total_look_price__gt = threshold)

    if 'average_item_price' and 'average_item_price_comparison' in request.data:
        comparison = request.data['average_item_price_comparison']
        threshold = request.data['average_item_price']
        if comparison == 'lt':
            lookmetrics = LookMetrics.objects.filter(average_item_price__lt = threshold)
        elif comparison == 'lte':
            lookmetrics = LookMetrics.objects.filter(average_item_price__lte = threshold)
        elif comparison == 'e':
            lookmetrics = LookMetrics.objects.filter(average_item_price = threshold)
        elif comparison == 'gte':
            lookmetrics = LookMetrics.objects.filter(average_item_price__gte = threshold)
        elif comparison == 'gt':
            lookmetrics = LookMetrics.objects.filter(average_item_price__gt = threshold)

    # do this step after filtering on potentially both total look price and average item price
    lookmetrics = lookmetrics.values_list('look', flat=True)
    # print lookmetrics

    looks = looks.filter(id__in = lookmetrics)


# we can traverse LookMetrics to get the Look that it is foreign key'd to
# e.g. LookMetrics.objects.filter(look__id__lte=2)
# but the opposite call yields an error
# e.g. Look.objects.filter(lookmetrics__id=1)

# django allows the traversal of foreign key relationships backwards but only for a given object instance
# aka, Look.lookmetrics_set

# use LookMetrics.objects.all() to build a query set of looks and use that query set as the filter
# that will be used in the filter chaining looks = looks.filter?

# Entry.objects.filter(id__gt=4)
    
    # lookmetrics = LookMetrics.objects.all() # refer to the 'client' case and 'favorites_only'

    # # LookMetrics.objects.filter(average_item_price__gte=3000)

    # # filter by average_item_price
    # if 'average_item_price' and 'comparison' in request.data:
    #     print 'this happens!!'
    #     if comparison == 'lt':
    #         print 'check'
    #     elif comparison == 'lte':
    #         print 'checkers'
    #     elif comparison == 'e':
    #         print 'cawfe'
    #     elif comparison == 'gte':
    #         print 'gween'
    #     elif comparison == 'gt':
    #         print 'tea'
    
    # if 'aip_filter' in request.data:
    #     aip_data = request.data['aip_filter']
    #     if 'average_item_price' in aip_data and 'comparison' in aip_data:
    #         threshold = aip_data['average_item_price']
    #         comparison = aip_data['comparison']
    #         # comparison case statements
    #         if comparison == 'lt':
    #             lookmetrics = LookMetrics.objects.filter(average_item_price__lt = threshold)
    #         elif comparison == 'lte':
    #             lookmetrics = LookMetrics.objects.filter(average_item_price__lte = threshold)
    #         elif comparison == 'e':
    #             lookmetrics = LookMetrics.objects.filter(average_item_price = threshold)
    #         elif comparison == 'gte':
    #             lookmetrics = LookMetrics.objects.filter(average_item_price__gte = threshold)
    #         elif comparison == 'gt':
    #             lookmetrics = LookMetrics.objects.filter(average_item_price__gte = threshold)

    # filter by total_look_price


    # after both the filter by total_look_price and average_item_price
    # looks = looks.filter(id__in = lookmetrics) # probably need to change?

    paginator = Paginator(looks, per_page)

    try:
        looks_paged = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        looks_paged = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        looks_paged = paginator.page(paginator.num_pages)

    serializer = LookSerializer(looks_paged, many=True)
    return JsonResponse({"num_pages": paginator.num_pages, "total_looks": paginator.count, "page": page, "per_page": per_page, "looks": serializer.data}, safe=False)

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
          "product": 393223,
          "layout_position": "xx,yy,zz"
        }

        Sample JSON Update Object
        URL: /shopping_tool_api/look_item/2/

        {
          "id": 2,
          "layout_position": 4,
          "look": 5,
          "product": 393223,
          "layout_position": "xx,yy,zz"
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
    layouts = LookLayout.objects.all()

    serializer = LookLayoutSerializer(layouts, many=True)
    return JsonResponse(serializer.data, safe=False)