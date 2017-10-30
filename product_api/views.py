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

# Create your views here.
