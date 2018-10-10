# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import ShippingPrice, MerchantDetail, Coupon, MerchantVisibility

############################################
# for merchant coupon editing
############################################
class CouponAdmin(admin.ModelAdmin):

    def has_add_permission(self, request, obj=None): # disable the add button
        return False

    def has_delete_permission(self, request, obj=None): # disable the delete button
        return False

    def get_queryset(self, request):
        qs = super(CouponAdmin, self).get_queryset(request)
        return qs.all().exclude(network=None)

    list_display = ('name', 'coupon_code', 'show_generic_coupon_message', 'coupon_description')
    list_editable = ['coupon_code', 'show_generic_coupon_message', 'coupon_description']
    search_fields = ('name',)
    readonly_fields = ['external_merchant_id', 'name', 'coupon_start_date', 'coupon_end_date',
    'network', 'active', 'created_at', 'updated_at', 'search_rank',
    'url_host', 'twotap_id', 
    'order_via_twotap_use_client_email'
    ] # not allow editing
    ordering = ('name',)

admin.site.register(Coupon, CouponAdmin)

############################################
# for merchant visibility editing
############################################
class VisibilityAdmin(admin.ModelAdmin):

    def has_add_permission(self, request, obj=None): # disable the add button
        return False

    def has_delete_permission(self, request, obj=None): # disable the delete button
        return False

    def get_queryset(self, request):
        qs = super(VisibilityAdmin, self).get_queryset(request)
        return qs.all().exclude(network=None)

    list_display = ('name', 'active', 'search_rank')
    list_editable = ['active', 'search_rank']
    search_fields = ('name',)
    readonly_fields = ['external_merchant_id', 'name', 'coupon_start_date', 'coupon_end_date',
    'network', 'active', 'created_at', 'updated_at', 'search_rank',
    'url_host', 'twotap_id', 
    'order_via_twotap_use_client_email'
    ] # not allow editing
    ordering = ('name',)

admin.site.register(MerchantVisibility, VisibilityAdmin)

############################################
# for full merchant editing
############################################
class MerchantDetailAdmin(admin.ModelAdmin):

    def has_add_permission(self, request, obj=None): # disable the add button
        return False

    def has_delete_permission(self, request, obj=None): # disable the delete button
        return False

    def get_queryset(self, request):
        qs = super(MerchantDetailAdmin, self).get_queryset(request)
        return qs.all().exclude(network=None)
    
    list_display = ('name', 'active', 'search_rank', 'coupon_code', 'show_generic_coupon_message', 'coupon_description', 'order_via_twotap','two_tap_supported', 'twotap_feed_enable', 'never_used_feed', 'final_sale', 'shipping_policy', 'network')
    search_fields = ('name',)
    readonly_fields = ['external_merchant_id', 'name', 'coupon_start_date', 'coupon_end_date',
    'network', 'created_at', 'updated_at',  
    ] # not allow editing
    ordering = ('name',)

admin.site.register(MerchantDetail, MerchantDetailAdmin)

############################################
# for shipping price editing
############################################
class ShippingPriceAdmin(admin.ModelAdmin):

    list_display = ('merchant', 'min_threshold', 'threshold', 'amount')
    list_editable = ['min_threshold',  'threshold', 'amount']
    search_fields = ('merchant_id__name',)
    ordering = ('merchant__name', 'min_threshold')

    # only get the merchants with network_id
    def get_queryset(self, request):
        qs = super(ShippingPriceAdmin, self).get_queryset(request)
        return qs.all().exclude(merchant__network=None)

    # this way allows selecting merchant when adding, but not allow changing the merchant afterward
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['merchant']
        else:
            return []

admin.site.register(ShippingPrice, ShippingPriceAdmin)