# -*- coding: utf-8 -*-
from __future__ import unicode_literals
<<<<<<< HEAD
from shopping_tool.models import WpUser
=======
from shopping_tool.models import WpUsers
>>>>>>> 09909669f33c3392509e59c85d3972a6afeeaeeb

from django.db.models.functions import Concat
from django.db.models import Value

from .serializers import StylistProfileSerializer

from rest_framework.response import Response
from rest_framework.decorators import (api_view, renderer_classes, permission_classes)
from rest_framework.views import APIView
from shopping_tool.decorators import check_login
<<<<<<< HEAD
=======
from django.views.decorators.csrf import csrf_exempt
>>>>>>> 09909669f33c3392509e59c85d3972a6afeeaeeb

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
<<<<<<< HEAD
            return WpUser.objects.none()

        # qs = WpUser.objects.all() # for first_name search only
        qs = WpUser.objects.annotate(fullname=Concat('first_name', Value(' '), 'last_name'))
=======
            return WpUsers.objects.none()

        # qs = WpUsers.objects.all() # for first_name search only
        qs = WpUsers.objects.annotate(fullname=Concat('first_name', Value(' '), 'last_name'))
>>>>>>> 09909669f33c3392509e59c85d3972a6afeeaeeb

        if self.q:
            # qs = qs.filter(first_name__istartswith=self.q) # for first_name search only
            qs = qs.filter(fullname__istartswith=self.q)
        return qs

########################################################
# API to create new stylist
########################################################
@api_view(['POST'])
@check_login
<<<<<<< HEAD
=======
@csrf_exempt
>>>>>>> 09909669f33c3392509e59c85d3972a6afeeaeeb
def create_new_stylist(requests):
    try:
        serializer = StylistProfileSerializer(data=requests.data)
        if serializer.is_valid():
            serializer.create(serializer.validated_data, requests)
            return JsonResponse({'status':'success', 'data':[]}, status=200)
        else:
            return JsonResponse({'status': 'missing required attributes', 'data':[]}, status=400)
    except IntegrityError as exception:
        return JsonResponse({'status': 'failed, stylist already in system', 'data':[]}, status=400)
    except:
        return JsonResponse({'status': 'failed with unknown reason', 'data':[]}, status=500)