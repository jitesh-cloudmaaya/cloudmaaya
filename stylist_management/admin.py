# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Register your models here.
from .models import StylistProfile, StylistRole, ClientTier, StylistManagement
from .forms import PersonForm

from django_extensions.admin import ForeignKeyAutocompleteAdmin

admin.site.register(ClientTier)
admin.site.register(StylistRole)

# for stylist page
class StylistProfileAdmin(admin.ModelAdmin):

    def has_add_permission(self, request, obj=None): # disable the add button
        return False

    def get_queryset(self, request):
        qs = super(StylistProfileAdmin, self).get_queryset(request)
        return qs.filter(role='Stylist')

    list_display = ('stylist_id', 'stylist', 'email', 'phone', 'director', 'manager', 'asm', 'role', 'on_duty', 'on_board', 'client_tier', 'start_date', 'off_board_date', 'pay_rate', 'birthday')
    search_fields = ('stylist__last_name', 'stylist__first_name', 'director__first_name', 'director__last_name', 'manager__first_name', 'manager__last_name', 'asm__first_name', 'asm__last_name')
    list_filter = ('on_duty', 'on_board', 'client_tier')
    readonly_fields = ['stylist_id', 'stylist', 'email', 'phone'] # not allow editing of stylist info
    def email(self, obj):
        return obj.stylist.user_email
    def phone(self, obj):
        return obj.stylist.user_phone # changed it was user_phone
    form = PersonForm

admin.site.register(StylistProfile, StylistProfileAdmin)


# for management page
class StylistManagementAdmin(admin.ModelAdmin):

    def has_add_permission(self, request, obj=None): # disable the add button
        return False

    def get_queryset(self, request):
        qs = super(StylistManagementAdmin, self).get_queryset(request)
        return qs.all().exclude(role='Stylist')

    list_display = ('stylist_id', 'stylist', 'email', 'phone', 'director', 'manager', 'asm', 'role', 'on_duty', 'on_board', 'client_tier', 'start_date', 'off_board_date', 'pay_rate', 'birthday')
    search_fields = ('stylist__last_name', 'stylist__first_name', 'director__first_name', 'director__last_name', 'manager__first_name', 'manager__last_name', 'asm__first_name', 'asm__last_name')
    list_filter = ('role',)
    readonly_fields = ['stylist_id', 'stylist', 'email', 'phone'] # not allow editing of stylist info
    def email(self, obj):
        return obj.stylist.user_email # changed
    def phone(self, obj):
        return obj.stylist.user_phone # changed
    form = PersonForm

admin.site.register(StylistManagement, StylistManagementAdmin)