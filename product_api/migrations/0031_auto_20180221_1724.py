# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-02-21 17:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_api', '0030_auto_20180215_0033'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['primary_category'], name='product_api_primary_9003d9_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['secondary_category'], name='product_api_seconda_697483_idx'),
        ),
    ]