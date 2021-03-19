# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-10-10 06:22
from __future__ import unicode_literals

from django.db import migrations, models

import sys

class Migration(migrations.Migration):

    # Escaping Alter column SQL for tests with SQLLite
    if 'test' in sys.argv:
        product_SQL = "SELECT COUNT(1)"                      
    else:
        product_SQL = """ALTER TABLE `product_api_product` 
                         MODIFY `age` varchar(50) NULL, 
                         MODIFY `allume_size` varchar(100) NULL,
                         MODIFY `buy_url` varchar(500) NULL,
                         MODIFY `color` varchar(50) NULL,
                         MODIFY `gender` varchar(50) NULL,
                         MODIFY `manufacturer_name` varchar(100) NULL,
                         MODIFY `merchant_name` varchar(100) NULL,
                         MODIFY `product_image_url` varchar(500) NULL,
                         MODIFY `raw_product_url` varchar(500) NULL
                """

    dependencies = [
        ('product_api', '0053_auto_20180929_0656'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_id', models.BigIntegerField(blank=True, db_index=True, null=True)),
                ('merchant_id', models.BigIntegerField(blank=True, db_index=True, null=True)),
                ('product_name', models.CharField(blank=True, max_length=255, null=True)),
                ('long_product_description', models.CharField(blank=True, max_length=2000, null=True)),
                ('short_product_description', models.CharField(blank=True, max_length=500, null=True)),
                ('product_url', models.CharField(blank=True, max_length=2000, null=True)),
                ('raw_product_url', models.CharField(blank=True, max_length=500, null=True)),
                ('product_image_url', models.CharField(blank=True, max_length=500, null=True)),
                ('buy_url', models.CharField(blank=True, max_length=500, null=True)),
                ('manufacturer_name', models.CharField(blank=True, max_length=100, null=True)),
                ('manufacturer_part_number', models.CharField(blank=True, max_length=50, null=True)),
                ('sku', models.CharField(blank=True, db_column='SKU', max_length=64, null=True)),
                ('product_type', models.CharField(blank=True, max_length=128, null=True)),
                ('discount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('discount_type', models.CharField(blank=True, max_length=10, null=True)),
                ('sale_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('retail_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('shipping_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('color', models.CharField(blank=True, max_length=50, null=True)),
                ('gender', models.CharField(blank=True, max_length=50, null=True)),
                ('style', models.CharField(blank=True, max_length=128, null=True)),
                ('size', models.CharField(blank=True, max_length=128, null=True)),
                ('material', models.CharField(blank=True, max_length=128, null=True)),
                ('age', models.CharField(blank=True, max_length=50, null=True)),
                ('currency', models.CharField(blank=True, max_length=3, null=True)),
                ('begin_date', models.DateTimeField(blank=True, null=True)),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('merchant_name', models.CharField(blank=True, max_length=100, null=True)),
                ('keywords', models.CharField(blank=True, max_length=1000, null=True)),
                ('primary_category', models.CharField(blank=True, max_length=500, null=True)),
                ('secondary_category', models.CharField(blank=True, max_length=500, null=True)),
                ('allume_score', models.IntegerField(blank=True, null=True)),
                ('is_trending', models.BooleanField(default=0)),
                ('is_best_seller', models.BooleanField(default=0)),
                ('brand', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('availability', models.CharField(blank=True, max_length=50, null=True)),
                ('is_deleted', models.BooleanField(default=0)),
                ('current_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('allume_size', models.CharField(blank=True, max_length=100, null=True)),
                ('allume_category', models.CharField(blank=True, max_length=128, null=True)),
                ('merchant_color', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),

        migrations.RunSQL(product_SQL),

        migrations.AddIndex(
            model_name='producthistory',
            index=models.Index(fields=['allume_category'], name='product_api_allume__f66692_idx'),
        ),
        migrations.AddIndex(
            model_name='producthistory',
            index=models.Index(fields=['primary_category', 'secondary_category'], name='product_api_primary_083407_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='producthistory',
            unique_together=set([('product_id', 'merchant_id')]),
        ),
]