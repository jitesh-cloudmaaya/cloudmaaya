# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

<<<<<<< HEAD
from .models import LookLayout, StyleOccasion, StyleType, WpUser
=======
from .models import LookLayout, StyleOccasion, StyleType, WpUsers
>>>>>>> 09909669f33c3392509e59c85d3972a6afeeaeeb

# Register your models here.

class StyleTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'updated_at')
    fields = ('name', 'active')

class StyleOccasionAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'updated_at')
    fields = ('name', 'active')

admin.site.register(StyleType, StyleTypeAdmin)
admin.site.register(StyleOccasion, StyleOccasionAdmin)

<<<<<<< HEAD
# Add WpUser as user admin
admin.site.register(WpUser, UserAdmin)
=======
# Add WpUsers as user admin
# admin.site.register(WpUsers, UserAdmin)
>>>>>>> 09909669f33c3392509e59c85d3972a6afeeaeeb



