# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Order_Job

class Order_Job_Admin(admin.ModelAdmin):

    list_display = ('ID', 'status', 'reason', 'allume_cart_id', 'date_created', 'link')
    search_fields = ('name',)
    readonly_fields = ['ID', 'reason', 'detail', 'allume_cart_id', 'clickable', 'date_created'] # not allow editing
    list_filter = ('status', 'reason')
    ordering = ('-date_created',)

    def link(self, obj):
        return '<a href="%s">%s</a>' % (obj.clickable, obj.clickable)

    def has_add_permission(self, request, obj=None): # disable the add button
        return False

    def has_delete_permission(self, request, obj=None): # disable the delete button
        return False

    link.allow_tags = True

admin.site.register(Order_Job, Order_Job_Admin)