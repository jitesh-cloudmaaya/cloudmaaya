# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import LookLayout, StyleOccasion, StyleType

# Register your models here.

class StyleTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'updated_at')
    fields = ('name', 'active')

class StyleOccasionAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'updated_at')
    fields = ('name', 'active')

admin.site.register(StyleType, StyleTypeAdmin)
admin.site.register(StyleOccasion, StyleOccasionAdmin)



