# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.template.context_processors import csrf
from decorators import check_login
from django.core.exceptions import PermissionDenied
from .models import AllumeClients

# Create your views here.

@check_login
def index(request):
    user = request.user
    client = AllumeClients.objects.get(id=227)
    context = {'user': user, 'client': client}
    return render(request, 'shopping_tool/index.html', context)



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