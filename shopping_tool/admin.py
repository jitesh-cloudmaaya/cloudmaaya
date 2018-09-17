# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import LookLayout, StyleOccasion, StyleType, WpUser

# Register your models here.

class StyleTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'updated_at')
    fields = ('name', 'active')

class StyleOccasionAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'updated_at')
    fields = ('name', 'active')

admin.site.register(StyleType, StyleTypeAdmin)
admin.site.register(StyleOccasion, StyleOccasionAdmin)

# Add WpUser as user admin
admin.site.register(WpUser, UserAdmin)



