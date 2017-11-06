# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.template.context_processors import csrf

# Create your views here.

def index(request):
	context = {}
	return render(request, 'shopping_tool/index.html', context)
