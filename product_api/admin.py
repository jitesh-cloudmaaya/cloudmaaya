# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import *
from django.contrib.admin import SimpleListFilter


# Register your models here.

class CategoryMap_MerchantFilter(SimpleListFilter):
    title = 'Merchant' # or use _('country') for translated title
    parameter_name = 'merchant_name'

    def lookups(self, request, model_admin):
        cats = model_admin.model.objects.filter(merchant_name__isnull=False).all().order_by('merchant_name')
        merchants_list = []
        for cat in cats:
        	for merch in cat.merchant_name.split('|'):
        		merchants_list.append(merch)

        merchants_list.sort()
        merchants = set(merchants_list)

        merch_tuples_list = []
        for merchant in merchants:
        	print merchant
        	merch_tuples_list.append((merchant, merchant))

        merch_tuples_list.sort()

        return sorted(merch_tuples_list)

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(merchant_name__contains=self.value())


class ColorMapAdmin(admin.ModelAdmin):
    list_display = ('allume_color', 'external_color')
    list_filter = ('allume_color',)


class MerchantAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'network')
    list_filter = ('network',)

class NetworkAdmin(admin.ModelAdmin):
    list_display = ('name', 'active')

class CategoryMapAdmin(admin.ModelAdmin):
    list_display = ('id', 'external_cat1', 'external_cat2', 'merchant_name_formatted', 'allume_category', 'turned_on', 'pending_review')
    list_filter = ('pending_review', 'turned_on', 'allume_category', CategoryMap_MerchantFilter,)
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
admin.site.register(ColorMap, ColorMapAdmin)

