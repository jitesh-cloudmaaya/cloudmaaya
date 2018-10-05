# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import LookLayout, StyleOccasion, StyleType, WpUsers, LookCopy
from admin_views.admin import AdminViews

# Register your models here.

class StyleTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'updated_at')
    fields = ('name', 'active')

class StyleOccasionAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'updated_at')
    fields = ('name', 'active')

admin.site.register(StyleType, StyleTypeAdmin)
admin.site.register(StyleOccasion, StyleOccasionAdmin)

# Add WpUsers as user admin
# admin.site.register(WpUsers, UserAdmin)


class LookCopyAdmin(AdminViews):
    list_display = ('from_look_id', 'to_look_id', 'from_stylist_id', 'to_stylist_id')
    admin_views = (
                    ('Download Look Copy Detail Report', '/shopping_tool_api/look_copy_report'),
        )

admin.site.register(LookCopy, LookCopyAdmin)


