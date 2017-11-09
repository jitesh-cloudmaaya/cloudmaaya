# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.


class RanProducts(models.Model):
    product_id = models.BigIntegerField(blank=True, null=True, db_index=True)
    product_name = models.CharField(max_length=255, blank=True, null=True)
    sku = models.CharField(db_column='SKU', max_length=64, blank=True, null=True)  # Field name made lowercase.
    primary_category = models.CharField(max_length=150, blank=True, null=True, db_index=True)
    secondary_category = models.CharField(max_length=500, blank=True, null=True, db_index=True)
    product_url = models.CharField(max_length=2000, blank=True, null=True)
    product_image_url = models.CharField(max_length=2000, blank=True, null=True)
    buy_url = models.CharField(max_length=2000, blank=True, null=True)
    short_product_description = models.CharField(max_length=500, blank=True, null=True)
    long_product_description = models.CharField(max_length=2000, blank=True, null=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    discount_type = models.CharField(max_length=10, blank=True, null=True)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    retail_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    begin_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    brand = models.CharField(max_length=255, blank=True, null=True)
    shippping = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    keywords = models.CharField(max_length=1000, blank=True, null=True)
    manufacturer_part_number = models.CharField(max_length=50, blank=True, null=True)
    manufacturer_name = models.CharField(max_length=250, blank=True, null=True)
    shipping_information = models.CharField(max_length=50, blank=True, null=True)
    availablity = models.CharField(max_length=50, blank=True, null=True)
    universal_product_code = models.CharField(max_length=15, blank=True, null=True)
    class_id = models.IntegerField(blank=True, null=True)
    currency = models.CharField(max_length=3, blank=True, null=True)
    m1 = models.CharField(db_column='M1', max_length=2000, blank=True, null=True)  # Field name made lowercase.
    pixel = models.CharField(max_length=128, blank=True, null=True)
    attribute_1_misc = models.CharField(max_length=128, blank=True, null=True)
    attribute_2_product_type = models.CharField(max_length=128, blank=True, null=True)
    attribute_3_size = models.CharField(max_length=128, blank=True, null=True)
    attribute_4_material = models.CharField(max_length=128, blank=True, null=True)
    attribute_5_color = models.CharField(max_length=128, blank=True, null=True)
    attribute_6_gender = models.CharField(max_length=128, blank=True, null=True)
    attribute_7_style = models.CharField(max_length=128, blank=True, null=True)
    attribute_8_age = models.CharField(max_length=128, blank=True, null=True)
    attribute_9 = models.CharField(max_length=128, blank=True, null=True)
    attribute_10 = models.CharField(max_length=128, blank=True, null=True)
    attribute_11 = models.CharField(max_length=128, blank=True, null=True)
    attribute_12 = models.CharField(max_length=128, blank=True, null=True)
    attribute_13 = models.CharField(max_length=128, blank=True, null=True)
    attribute_14 = models.CharField(max_length=128, blank=True, null=True)
    attribute_15 = models.CharField(max_length=128, blank=True, null=True)
    attribute_16 = models.CharField(max_length=128, blank=True, null=True)
    attribute_17 = models.CharField(max_length=128, blank=True, null=True)
    attribute_18 = models.CharField(max_length=128, blank=True, null=True)
    attribute_19 = models.CharField(max_length=128, blank=True, null=True)
    attribute_20 = models.CharField(max_length=128, blank=True, null=True)
    attribute_21 = models.CharField(max_length=128, blank=True, null=True)
    attribute_22 = models.CharField(max_length=128, blank=True, null=True)
    modification = models.CharField(max_length=128, blank=True, null=True)
    merchant_id = models.IntegerField(blank=True, null=True, db_index=True)
    merchant_name = models.CharField(max_length=75, blank=True, null=True)

    #class Meta:
    #    managed = False