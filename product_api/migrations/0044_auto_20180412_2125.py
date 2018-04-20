# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-04-12 21:25
from __future__ import unicode_literals

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('product_api', '0043_merge_20180412_1952'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='product',
            name='product_api_primary_9003d9_idx',
        ),
        migrations.RemoveIndex(
            model_name='product',
            name='product_api_seconda_697483_idx',
        ),
        migrations.AlterField(
            model_name='product',
            name='allume_category',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['primary_category', 'secondary_category'], name='product_api_primary_26aa77_idx'),
        ),
        #migrations.RunSQL("ALTER TABLE product_api_product convert to CHARSET latin1;"),
    ]