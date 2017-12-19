# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import *

# Register your models here.

class MerchanttInLine(admin.TabularInline):
    model = Merchant
    extra = 0

class NetworkInLine(admin.TabularInline):
    model = Network
    extra = 0

class MerchantCategoryInLine(admin.TabularInline):
    model = MerchantCategory
    extra = 0 

admin.site.register(Merchant)
admin.site.register(Network)
admin.site.register(MerchantCategory)


