# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from shopping_tool.models import WpUsers, AllumeWpUserStylingRoles

from django.db.models.functions import Concat
from django.db.models import Value

from .serializers import StylistProfileSerializer

from rest_framework.response import Response
from rest_framework.decorators import (api_view, renderer_classes, permission_classes)
from rest_framework.views import APIView
from shopping_tool.decorators import check_login
from django.views.decorators.csrf import csrf_exempt

from django.http import HttpResponseRedirect, HttpResponse, JsonResponse

from django.db import IntegrityError

########################################################
# Autocomplete API to search for stylists when editing
########################################################
from dal import autocomplete
class UserAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return WpUsers.objects.none()

        # qs = WpUsers.objects.all() # for first_name search only
        # qs = WpUsers.objects.annotate(fullname=Concat('first_name', Value(' '), 'last_name')) # for search for all wpuser

        # temporaryly search for the persons in the allume_wp_user_styling_roles table        
        qs = WpUsers.objects.filter(allumewpuserstylingroles__isnull=False).annotate(fullname=Concat('first_name', Value(' '), 'last_name'))

        if self.q:
            qs = qs.filter(fullname__istartswith=self.q)
        return qs

########################################################
# API to create new stylist
########################################################
@api_view(['POST'])
@check_login
@csrf_exempt
def create_new_stylist(requests):
    try:
        serializer = StylistProfileSerializer(data=requests.data)
        if serializer.is_valid():
            serializer.create(serializer.validated_data)
            return JsonResponse({'status':'success', 'data':[]}, status=200)
        else:
            return JsonResponse({'status': 'missing required attributes', 'data':[]}, status=400)
    except IntegrityError as exception:
        return JsonResponse({'status': 'failed, data integrity error (stylist already in system or wrong role_id / client_tier / director_manager_asm_id)', 'data':[]}, status=400)
    except:
        return JsonResponse({'status': 'failed with unknown reason', 'data':[]}, status=500)

# off board stylist
@api_view(['POST'])
@check_login
@csrf_exempt
def off_board_stylist(requests):
    try:
        serializer = StylistProfileSerializer(data=requests.data)
        if serializer.is_valid():
            serializer.off_board(serializer.validated_data)
            return JsonResponse({'status':'success', 'data':[]}, status=200)
        else:
            return JsonResponse({'status': 'missing required attributes', 'data':[]}, status=400)
    except:
        return JsonResponse({'status': 'failed with unknown reason', 'data':[]}, status=500)