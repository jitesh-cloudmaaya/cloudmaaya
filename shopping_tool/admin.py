# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import LookLayout

# Register your models here.

class LookLayoutInLine(admin.TabularInline):
    model = LookLayout
    extra = 0

admin.site.register(LookLayout)
