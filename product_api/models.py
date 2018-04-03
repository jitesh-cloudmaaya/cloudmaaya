# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import json
from catalogue_service.settings import BASE_DIR
from django.db import models
from rest_framework import serializers
import json
import urllib2
import requests
from catalogue_service.settings_local import ENV_LOCAL, ALLUME_API_AUTH_USER, ALLUME_API_AUTH_PASS
from requests.auth import HTTPBasicAuth
from django.db.models.signals import pre_save
from django.dispatch import receiver

# Create your models here.

class Product(models.Model):
    product_id = models.BigIntegerField(blank=True, null=True, db_index=True)
    merchant_id = models.BigIntegerField(blank=True, null=True, db_index=True)
    product_name = models.CharField(max_length=255, blank=True, null=True)
    long_product_description = models.CharField(max_length=2000, blank=True, null=True)
    short_product_description = models.CharField(max_length=500, blank=True, null=True)
    product_url = models.CharField(max_length=2000, blank=True, null=True)
    raw_product_url = models.CharField(max_length=2000, blank=True, null=True)
    product_image_url = models.CharField(max_length=2000, blank=True, null=True)
    buy_url = models.CharField(max_length=2000, blank=True, null=True)
    manufacturer_name = models.CharField(max_length=250, blank=True, null=True)
    manufacturer_part_number = models.CharField(max_length=50, blank=True, null=True)
    sku = models.CharField(db_column='SKU', max_length=64, blank=True, null=True)  # Field name made lowercase.
    product_type = models.CharField(max_length=128, blank=True, null=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    discount_type = models.CharField(max_length=10, blank=True, null=True)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    retail_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    shipping_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    color = models.CharField(max_length=128, blank=True, null=True)
    gender = models.CharField(max_length=128, blank=True, null=True)
    style = models.CharField(max_length=128, blank=True, null=True)
    size = models.CharField(max_length=128, blank=True, null=True)
    material = models.CharField(max_length=128, blank=True, null=True)
    age = models.CharField(max_length=128, blank=True, null=True)
    currency = models.CharField(max_length=3, blank=True, null=True)
    begin_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    merchant_name = models.CharField(max_length=2000, blank=True, null=True)
    keywords = models.CharField(max_length=1000, blank=True, null=True)
    primary_category = models.CharField(max_length=500, blank=True, null=True)
    secondary_category = models.CharField(max_length=500, blank=True, null=True)
    allume_score = models.IntegerField(blank=True, null=True)
    is_trending = models.BooleanField(default=0)
    is_best_seller = models.BooleanField(default=0)
    brand = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    availability = models.CharField(max_length=50, blank=True, null=True)
    is_deleted = models.BooleanField(default=0)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    allume_size = models.CharField(max_length=255, blank=True, null=True)
    allume_category = models.CharField(max_length=255, blank=True, null=True)
    merchant_color = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = (('product_id', 'merchant_id'))
        indexes = [
            models.Index(fields=['primary_category']),
            models.Index(fields=['secondary_category']),
            models.Index(fields=['allume_category']),
            models.Index(fields=['merchant_id']),
        ]

class Network(models.Model):
    name = models.CharField(max_length=128, blank=True, null=True)
    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name

class Merchant(models.Model):
    external_merchant_id = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=128, blank=True, null=True)
    network = models.ForeignKey(Network)
    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)


    def __str__(self):
        return self.name

    ## Used to Update the Allume API ##
    def update_allume_status(self):
        data = {"affiliate_feed_external_merchant_url_host": "NONE",
                "affiliate_feed_merchant_id": self.id,
                "active": self.active,
                "affiliate_feed_external_merchant_id": self.external_merchant_id,
                "affiliate_feed_network_id": self.network_id,
                "affiliate_feed_external_merchant_name": self.name
                }

        api_url = "https://styling-service-%s.allume.co/update_retailer_info/" % (ENV_LOCAL)
        response = requests.post(api_url, json=data, auth=HTTPBasicAuth(ALLUME_API_AUTH_USER, ALLUME_API_AUTH_PASS))

        print response.content

        if json.loads(response.content)['status'] == "success":
            return True
        else:
            return False

    class Meta:
        indexes = [
            models.Index(fields=['name'])
        ]

class MerchantCategory(models.Model):
    external_merchant_id = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=128, blank=True, null=True)
    network = models.ForeignKey(Network)
    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Merchant Categories"

class ColorMap(models.Model):
    external_color = models.CharField(max_length=128, blank=True, null=True)
    allume_color = models.CharField(max_length=128, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.external_color

class AllumeCategory(models.Model):
    name = models.CharField(max_length=128, blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    position = models.IntegerField(default=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Allume Categories"
        indexes = [
            models.Index(fields=['name'])
        ]

class CategoryMap(models.Model):
    external_cat1 = models.CharField(max_length=500, blank=True, null=True)
    external_cat2 = models.CharField(max_length=500, blank=True, null=True)
    allume_category = models.ForeignKey(AllumeCategory, blank=True, null=True)
    turned_on = models.BooleanField(default=False, db_column='active')
    pending_review = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    merchant_name = models.CharField(max_length=2000, blank=True, null=True)

    def __str__(self):
        return self.external_cat1 + ": " + self.external_cat2

    def merchant_name_formatted(self):
        if self.merchant_name != None:
            return self.merchant_name.replace("|", ", ")
        else:
            return self.merchant_name

    class Meta:
        indexes = [
            models.Index(fields=['external_cat1']),
            models.Index(fields=['external_cat2']),
        ]

# used in parsing category strings for the presence of a SynonymCategoryMap.synonym
class SynonymCategoryMap(models.Model):
    synonym = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.synonym

# used in parsing category strings for exclusion terms
class ExclusionTerm(models.Model):
    term = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.term

# used in parsing category strings for terms that should map to allume category, Other
class OtherTermMap(models.Model):
    term = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.term

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


@receiver(pre_save, sender=Merchant)
def update_allume_merchant_pre_save(sender, instance, *args, **kwargs):

    #Skip if ENV <> Stage or Prod (So Circle Ci and Dev can function)
    if (ENV_LOCAL == 'stage') or (ENV_LOCAL == 'prod'):
        if not instance.update_allume_status() :
            raise Exception('Allume API Update Failed')

sizemap_filepath = os.path.join(BASE_DIR, 'product_api/models_config/SizeMap.json')
shoesizemap_filepath = os.path.join(BASE_DIR, 'product_api/models_config/ShoeSizeMap.json')
sizetermmap_filepath = os.path.join(BASE_DIR, 'product_api/models_config/SizeTermMap.json')

sizemap_attrs = json.load(open(sizemap_filepath, 'r'))
for attr in sizemap_attrs:
    sizemap_attrs[attr] = eval(sizemap_attrs[attr])
sizemap_attrs['__module__'] = 'product_api.models'

shoesizemap_attrs = json.load(open(shoesizemap_filepath, 'r'))
for attr in shoesizemap_attrs:
    shoesizemap_attrs[attr] = eval(shoesizemap_attrs[attr])
shoesizemap_attrs['__module__'] = 'product_api.models'

sizetermmap_attrs = json.load(open(sizetermmap_filepath, 'r'))
for attr in sizetermmap_attrs:
    sizetermmap_attrs[attr] = eval(sizetermmap_attrs[attr])
sizetermmap_attrs['__module__'] = 'product_api.models'

SizeMap = type(str("SizeMap"), (models.Model,), sizemap_attrs)
ShoeSizeMap = type(str("ShoeSizeMap"), (models.Model,), shoesizemap_attrs)
SizeTermMap = type(str("SizeTermMap"), (models.Model,), sizetermmap_attrs)
