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
    primary_category = models.CharField(max_length=150, blank=True, null=True)
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
            # models.Index(fields=['allume_category']),
            # models.Index(fields=['merchant_name']),
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

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Allume Categories"
        indexes = [
            models.Index(fields=['name'])
        ]

class CategoryMap(models.Model):
    external_cat1 = models.CharField(max_length=150, blank=True, null=True)
    external_cat2 = models.CharField(max_length=500, blank=True, null=True)
    allume_category = models.ForeignKey(AllumeCategory, blank=True, null=True)
    active = models.BooleanField(default=False)
    pending_review = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    merchant_name = models.CharField(max_length=2000, blank=True, null=True)

    def __str__(self):
        return self.external_cat1 + ": " + self.external_cat2

    class Meta:
        indexes = [
            models.Index(fields=['external_cat1']),
            models.Index(fields=['external_cat2']),
        ]

class SizeMap(models.Model):
    merchant_size = models.CharField(max_length=128, blank=True, null=True)
    allume_size = models.CharField(max_length=128, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.merchant_size

class ShoeSizeMap(models.Model):
    merchant_size = models.CharField(max_length=128, blank=True, null=True)
    allume_size = models.CharField(max_length=128, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.merchant_size

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


