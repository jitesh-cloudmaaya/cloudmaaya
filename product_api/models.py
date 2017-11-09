# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from rest_framework import serializers

# Create your models here.

class Product(models.Model):
    product_id = models.BigIntegerField(blank=True, null=True, db_index=True)
    merchant_id = models.BigIntegerField(blank=True, null=True, db_index=True)
    product_name = models.CharField(max_length=255, blank=True, null=True)
    long_product_description = models.CharField(max_length=2000, blank=True, null=True)
    short_product_description = models.CharField(max_length=500, blank=True, null=True)
    product_url = models.CharField(max_length=2000, blank=True, null=True)
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
    availability = models.CharField(max_length=50, blank=True, null=True)
    begin_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    merchant_name = models.CharField(max_length=2000, blank=True, null=True)
    keywords = models.CharField(max_length=55, blank=True, null=True)
    primary_category = models.CharField(max_length=150, blank=True, null=True)
    secondary_category = models.CharField(max_length=500, blank=True, null=True)
    allume_score = models.IntegerField(blank=True, null=True)
    is_trending = models.BooleanField(default=False)
    is_best_seller = models.BooleanField(default=False)
    brand = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class Network(models.Model):
    name = models.CharField(max_length=128, blank=True, null=True)
    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

class Merchant(models.Model):
    external_merchant_id = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=128, blank=True, null=True)
    network = models.ForeignKey(Network)
    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

class MerchantCategory(models.Model):
    external_merchant_id = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=128, blank=True, null=True)
    network = models.ForeignKey(Network)
    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

