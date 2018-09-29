# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import ShippingPrice, MerchantEditing


############################################
# for full merchant editing
############################################
class MerchantEditingAdmin(admin.ModelAdmin):

    def has_add_permission(self, request, obj=None): # disable the add button
        return False

    def has_delete_permission(self, request, obj=None): # disable the delete button
        return False

    def get_queryset(self, request):
        qs = super(MerchantEditingAdmin, self).get_queryset(request)
        return qs.all().exclude(network=None)

    list_display = ('name', 'coupon_code', 'show_generic_coupon_message', 'two_tap_supported')
    search_fields = ('name',)
    readonly_fields = ['external_merchant_id', 'name', 'coupon_start_date', 'coupon_end_date',
    'network', 'active', 'created_at', 'updated_at', 'search_rank',
    'url_host', 'twotap_id', 
    'order_via_twotap_use_client_email'
    ] # not allow editing

admin.site.register(MerchantEditing, MerchantEditingAdmin)

############################################
# for shipping price editing
############################################
class ShippingPriceAdmin(admin.ModelAdmin):

    list_display = ('merchant_id', 'min_threshold', 'threshold', 'amount')
    list_editable = ['min_threshold',  'threshold', 'amount']
    readonly_fields = ('merchant_id',)
    search_fields = ('merchant_id__name',)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['merchant_id']
        else:
            return []

admin.site.register(ShippingPrice, ShippingPriceAdmin)