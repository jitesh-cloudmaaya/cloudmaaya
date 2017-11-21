# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.template.context_processors import csrf
from decorators import check_login

# Create your views here.

@check_login
def index(request):
    user = request.user
    context = {'user': user}
    return render(request, 'shopping_tool/index.html', context)

def set_cookie(request):
    response_redirect = HttpResponseRedirect('/')
    response_redirect.set_cookie('username', 'wes')
    return response_redirect

def delete_cookie(request):
    response_redirect = HttpResponseRedirect('/')
    response_redirect.delete_cookie('username')
    return response_redirect