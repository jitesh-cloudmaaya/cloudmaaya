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
from .models import AllumeClients, Rack, AllumeStylingSessions, AllumeStylistAssignments, Look, LookLayout
from product_api.models import Product

# Create your views here. 

@check_login
def index(request):

    user = request.user
    layouts = LookLayout.objects.values()
    styling_session = AllumeStylingSessions.objects.get(id = 3)
    rack_items = Rack.objects.filter(allume_styling_session = styling_session)
    client = styling_session.client

    context = {'user': user, 'styling_session': styling_session, 'rack_items': rack_items, 'client': client, 'layouts': layouts}
    return render(request, 'shopping_tool/index.html', context)


########################################################
# Some Localdev Methods In Order to Test Login
# without Having Access to The WP Login Application
########################################################
def set_cookie(request):
    if request.get_host() in ['localhost:8000', '127.0.0.1:8000', 'shopping-tool-stage.allume.co']:
        response_redirect = HttpResponseRedirect('/')
        response_redirect.set_cookie('user_email', '1a80b36b569b69579b25ad4583b5c841allume.co')
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