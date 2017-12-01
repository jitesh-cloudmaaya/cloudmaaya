# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-06 05:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RanProductFeed',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_id', models.IntegerField(blank=True, null=True)),
                ('product_name', models.CharField(blank=True, max_length=255, null=True)),
                ('sku', models.CharField(blank=True, db_column='SKU', max_length=64, null=True)),
                ('primary_category', models.CharField(blank=True, max_length=50, null=True)),
                ('secondary_category', models.CharField(blank=True, max_length=500, null=True)),
                ('product_url', models.CharField(blank=True, max_length=2000, null=True)),
                ('product_image_url', models.CharField(blank=True, max_length=2000, null=True)),
                ('buy_url', models.CharField(blank=True, max_length=2000, null=True)),
                ('short_product_description', models.CharField(blank=True, max_length=500, null=True)),
                ('long_product_description', models.CharField(blank=True, max_length=2000, null=True)),
                ('discount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('discount_type', models.CharField(blank=True, max_length=10, null=True)),
                ('sale_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('retail_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('begin_date', models.DateTimeField(blank=True, null=True)),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('brand', models.CharField(blank=True, max_length=255, null=True)),
                ('shippping', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('keywords', models.CharField(blank=True, max_length=500, null=True)),
                ('manufacturer_part_number', models.CharField(blank=True, max_length=50, null=True)),
                ('manufacturer_name', models.CharField(blank=True, max_length=250, null=True)),
                ('shipping_information', models.CharField(blank=True, max_length=50, null=True)),
                ('availablity', models.CharField(blank=True, max_length=50, null=True)),
                ('universal_product_code', models.CharField(blank=True, max_length=15, null=True)),
                ('class_id', models.IntegerField(blank=True, null=True)),
                ('currency', models.CharField(blank=True, max_length=3, null=True)),
                ('m1', models.CharField(blank=True, db_column='M1', max_length=2000, null=True)),
                ('pixel', models.CharField(blank=True, max_length=128, null=True)),
                ('attribute_1_misc', models.CharField(blank=True, max_length=128, null=True)),
                ('attribute_2_product_type', models.CharField(blank=True, max_length=128, null=True)),
                ('attribute_3_size', models.CharField(blank=True, max_length=128, null=True)),
                ('attribute_4_material', models.CharField(blank=True, max_length=128, null=True)),
                ('attribute_5_color', models.CharField(blank=True, max_length=128, null=True)),
                ('attribute_6_gender', models.CharField(blank=True, max_length=128, null=True)),
                ('attribute_7_style', models.CharField(blank=True, max_length=128, null=True)),
                ('attribute_8_age', models.CharField(blank=True, max_length=128, null=True)),
                ('attribute_9', models.CharField(blank=True, max_length=128, null=True)),
                ('attribute_10', models.CharField(blank=True, max_length=128, null=True)),
                ('attribute_11', models.CharField(blank=True, max_length=128, null=True)),
                ('attribute_12', models.CharField(blank=True, max_length=128, null=True)),
                ('attribute_13', models.CharField(blank=True, max_length=128, null=True)),
                ('attribute_14', models.CharField(blank=True, max_length=128, null=True)),
                ('attribute_15', models.CharField(blank=True, max_length=128, null=True)),
                ('attribute_16', models.CharField(blank=True, max_length=128, null=True)),
                ('attribute_17', models.CharField(blank=True, max_length=128, null=True)),
                ('attribute_18', models.CharField(blank=True, max_length=128, null=True)),
                ('attribute_19', models.CharField(blank=True, max_length=128, null=True)),
                ('attribute_20', models.CharField(blank=True, max_length=128, null=True)),
                ('attribute_21', models.CharField(blank=True, max_length=128, null=True)),
                ('attribute_22', models.CharField(blank=True, max_length=128, null=True)),
                ('modification', models.CharField(blank=True, max_length=128, null=True)),
                ('merchant_id', models.IntegerField(blank=True, null=True)),
            ],
        ),
    ]
