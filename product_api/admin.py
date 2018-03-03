# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import *

# Register your models here.

class MerchantAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'network')

class NetworkAdmin(admin.ModelAdmin):
    list_display = ('name', 'active')

class CategoryMapAdmin(admin.ModelAdmin):
    list_display = ('id', 'external_cat1', 'external_cat2', 'merchant_name', 'allume_category', 'turned_on', 'pending_review')
    list_filter = ('pending_review', 'turned_on',)
    search_fields = ('external_cat1', 'external_cat2', 'allume_category__name', 'merchant_name')

#class MerchantCategoryAdmin(admin.ModelAdmin):
#    list_display = ('name', 'active', 'network')

class MerchantInLine(admin.TabularInline):

    model = Merchant
    extra = 0

class NetworkInLine(admin.TabularInline):
    model = Network
    extra = 0

#class MerchantCategoryInLine(admin.TabularInline):
#    model = MerchantCategory
#    extra = 0 

admin.site.register(Merchant, MerchantAdmin)
admin.site.register(Network, NetworkAdmin)
#admin.site.register(MerchantCategory, MerchantCategoryAdmin)
admin.site.register(CategoryMap, CategoryMapAdmin)
admin.site.register(AllumeCategory)
admin.site.register(ColorMap)


