# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
import requests
from django.shortcuts import redirect
from django.http import HttpResponse

# Create your views here.

def final_sale_check(requests, allume_cart_id):
    context = {'check': allume_cart_id}
    return render(requests, 'final_sale_check/index.html', context)

def proxy(request):
    url = request.GET['url']
    response = requests.get(url)
    response.headers['X-Frame-Options'] = 'ALLOWALL'
    return HttpResponse(response)