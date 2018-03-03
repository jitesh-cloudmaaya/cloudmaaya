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
from shopping_tool.models import AllumeClients, Rack, AllumeStylingSessions, AllumeStylistAssignments, AllumeUserStylistNotes
from shopping_tool.models import Look, LookLayout, LookProduct, UserProductFavorite, UserLookFavorite, AllumeClient360
from serializers import *
from rest_framework import status
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from tasks.product_feed_py.product_feed_helpers import determine_allume_size
from tasks.product_feed_py import mappings


@api_view(['POST'])
@permission_classes((AllowAny, ))
def get_allume_size(request):
    """
    post:
        Get Allume Size

        /shopping_tool_api/get_allume_size/      

        Sample JSON Object

        {
          "size": "x-small",
          "category": "Tops"
        }

    """

    size_mapping = mappings.create_size_mapping()
    shoe_size_mapping = mappings.create_shoe_size_mapping()
    size_term_mapping = mappings.create_size_term_mapping()
    allume_category = request.data['category']
    size = request.data['size'].upper()

    allume_size = determine_allume_size(allume_category, size, size_mapping, shoe_size_mapping, size_term_mapping)

    return JsonResponse(allume_size, safe=False)

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
def styling_session_note(request, pk=None):
    """
    get:
        View styling session Note

        /shopping_tool_api/styling_session_note/{note_id}/
    put:
        Add note to the styling session

        /shopping_tool_api/styling_session_note/0/

        Sample JSON Object

        {
          "stylist": 1,
          "client": 10,
          "styling_session": 393223,
          "notes": 393223,
          "visible": 11
        }

    delete:
        Remove a Note from the styling session        
    """
    if request.method == 'GET':
        try:
            note = AllumeUserStylistNotes.objects.get(id=pk)
        except AllumeUserStylistNotes.DoesNotExist:
            return HttpResponse(status=404)

        serializer = AllumeUserStylistNotesSerializer(note)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'PUT':

        try:
            note = AllumeUserStylistNotes.objects.get(id=pk)
            serializer = AllumeUserStylistNotesCreateSerializer(note, data=request.data)
        except AllumeUserStylistNotes.DoesNotExist:
            serializer = AllumeUserStylistNotesCreateSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        try:
            note = AllumeUserStylistNotes.objects.get(id = pk)
            note.delete()
            context = {'Success': True}
            return JsonResponse(context, status=status.HTTP_201_CREATED)
        except ObjectDoesNotExist as er:
            context = {'Success': False, 'Info': str(er)}
            return JsonResponse(context, status=status.HTTP_400_BAD_REQUEST)

        return Response(context) 

@api_view(['GET'])
@check_login
@permission_classes((AllowAny, ))
def styling_session_notes(request, pk=None):
    """
    get:
        View list of styling Session Notes

        /shopping_tool_api/styling_session_notes/{userid}/
    """
    try:
        notes = AllumeUserStylistNotes.objects.filter(client=pk).order_by('-last_modified').all()
    except AllumeUserStylistNotes.DoesNotExist:
        return HttpResponse(status=404)

    serializer = AllumeUserStylistNotesSerializer(notes, many=True)
    return JsonResponse(serializer.data, safe=False)


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


@api_view(['GET'])
@check_login
@permission_classes((AllowAny, ))
def style_type(request):
    """
    get:
        View list of style types

        /shopping_tool_api/style_type/
    """
    try:
        styles = StyleType.objects.filter(active=True).all()
    except StyleType.DoesNotExist:
        return HttpResponse(status=404)

    serializer = StyleTypeSerializer(styles, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
@check_login
@permission_classes((AllowAny, ))
def style_occasions(request):
    """
    get:
        View list of style occasions

        /shopping_tool_api/style_occasions/
    """
    try:
        styles = StyleOccasion.objects.filter(active=True).all()
    except StyleOccasion.DoesNotExist:
        return HttpResponse(status=404)

    serializer = StyleOccasionSerializer(styles, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(['PUT'])
@check_login
@permission_classes((AllowAny, ))
def look_meta_tags(request, pk=None):
    """
    put:
        Add Style and Occasion to Looks

        /shopping_tool_api/look_meta_tags/{look_id}/

        Sample JSON Object

        {
          "look_id": 393223,
          "style_type": [1,2,4],
          "style_occasion": [3,4]

        }
    """
    try:
        look = Look.objects.get(id=pk)
    except Look.DoesNotExist:
        return HttpResponse(status=404)

    print ("Deleting Meta")
    look.styleoccasion_set = []
    look.styletype_set = []

    print("Saving Occasion")
    look.styleoccasion_set = request.data['style_occasion']

    print("Savign Type")
    look.styletype_set = request.data['style_type']

    look.save()

    return JsonResponse(request.data, safe=False)

@api_view(['PUT'])
@check_login
@permission_classes((AllowAny, ))
def update_look_position(request, pk=None):
    """
    put:
        Edit the Position attribute of a Look.

        /shopping_tool_api/update_look_position/{look_id}/

        Sample JSON object
        {
          "look_id": 39223,
          "position": 4
        }
    """
    try:
        look = Look.objects.get(id=pk)
    except Look.DoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    # print("Setting new position")
    look.position = request.data['position']

    look.save()

    return JsonResponse(request.data, safe=False)

@api_view(['PUT'])
@check_login
@permission_classes((AllowAny, ))
def update_look_collage_image_data(request, pk=None):
    """
    put:
        Edit the collage_image_data field of an AllumeLooks.

        /shopping_tool_api/update_look_collage_image_data/{allumelooks_id}/

        Sample JSON object
        {
          "collage_image_data": "payload",
        }
    """
    try:
        look = Look.objects.get(id=pk)
    except Look.DoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    look.collage = request.data['collage_image_data']
    look.save()

    return JsonResponse(request.data, safe=False)

@api_view(['PUT'])
@check_login
@permission_classes((AllowAny, ))
def update_cropped_image_code(request, pk=None):
    """
    Update the cropped_image_code of a LookProduct.

    /shopping_tool_api/update_cropped_image_code/{lookproduct_id}/

    Sample JSON object
    {
        "cropped_image_code": "payload",
    }
    """
    try:
        lookproduct = LookProduct.objects.get(id=pk)
    except LookProduct.DoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    lookproduct.cropped_image_code = request.data['cropped_image_code']
    lookproduct.save()

    return JsonResponse(request.data, safe=False)

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
          "allume_styling_session": 3,
          "stylist": 1
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
        item = request.data

        if 'stylist' not in item:
            item['stylist'] = request.user.id

        serializer = RackCreateSerializer(data=item)
        

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

@api_view(['GET', 'PUT', 'DELETE'])
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
         "allume_styling_session":3,
         "stylist": 117,
         "description": "",
         "collage_image_data": ""
        }
    delete:
        Delete a look
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

    elif request.method == 'DELETE':
        try:
            look = Look.objects.get(id = pk)
            look.status = 'Deleted'
            look.save()
            context = {'Success': True}
            return JsonResponse(context, status=status.HTTP_201_CREATED)
        except ObjectDoesNotExist as er:
            context = {'Success': False, 'Info': str(er)}
            return JsonResponse(context, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@check_login
@permission_classes((AllowAny, ))
def look_list(request):
    """
    post:
        Get a list of looks filtered by shopper, client or styling_session and its products, layouts, etc
       
        Sample JSON Object, all filters below are optional, though both total_look_price and average_item_price
        expect to occur with a respective minimum and maximum.

        {
         "client": 1,
         "allume_styling_session":3,
         "stylist": 117,
         "name": "Body Suit",
         "page": 1,
         "per_page": 20,
         "favorites_only": True,
         "total_look_price_minimum": 500.00,
         "total_look_price_maximum": 1000.00,
         "average_item_price_minimum": 20.00,
         "average_item_price_maximum": 45.00,
         "show_deleted": True
          "style_type": [1,2,4],
          "style_occasion": [3,4]
        }
    """
    looks = Look.objects.all()  
    # looks = looks.filter(look_layout__isnull=False)
    # looks = looks.exclude(look_layout = 0)

    page = 1
    if 'page' in request.data:
        page = request.data['page']

    per_page = 20
    if 'per_page' in request.data:
        per_page = request.data['per_page']

    if 'show_deleted' in request.data:
        looks = looks
    else:
        looks = looks.exclude(status = 'Deleted')

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
        looks = looks.filter(Q(name__icontains = name) | Q(description__icontains = name))

    if 'favorites_only' in request.data:
        if request.data['favorites_only'] == "True":
            favs = UserLookFavorite.objects.filter(stylist=request.user.id).values_list('look_id', flat=True)
            looks = looks.filter(id__in = favs)

    if 'style_type' in request.data:
        looks = looks.filter(styletype__in = request.data['style_type'])

    if 'style_occasion' in request.data:
        looks = looks.filter(styleoccasion__in = request.data['style_occasion'])

    lookmetrics = LookMetrics.objects.all()
    if 'total_look_price_minimum' in request.data and 'total_look_price_maximum' in request.data:
        minimum = request.data['total_look_price_minimum']
        maximum = request.data['total_look_price_maximum']
        lookmetrics = LookMetrics.objects.filter(total_look_price__gte = minimum, total_look_price__lte = maximum)

    if 'average_item_price_minimum' in request.data and 'average_item_price_maximum' in request.data:
        minimum = request.data['average_item_price_minimum']
        maximum = request.data['average_item_price_maximum']
        lookmetrics = lookmetrics.filter(average_item_price__gte = minimum, average_item_price__lte = maximum)

    # do this step after filtering on potentially both total look price and average item price
    if 'total_look_price_minimum' in request.data or 'average_item_price_minimum' in request.data:
        lookmetrics = lookmetrics.values_list('look', flat=True)
        looks = looks.filter(id__in = lookmetrics)

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
          "layout_position": "xx,yy,zz",
          "cropped_dimensions": ""
        }

        Sample JSON Update Object
        URL: /shopping_tool_api/look_item/2/

        {
          "id": 2,
          "layout_position": 4,
          "look": 5,
          "product": 393223,
          "layout_position": "xx,yy,zz"
          "cropped_dimensions": ""
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

        item = request.data.copy()
        if 'product_clipped_stylist_id' not in item:
            item['product_clipped_stylist_id'] = request.user.id

        try:
            look_item = LookProduct.objects.get(id=pk)
            serializer = LookProductCreateSerializer(look_item, data=item)

        except LookProduct.DoesNotExist:
            serializer = LookProductCreateSerializer(data=item)
        
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