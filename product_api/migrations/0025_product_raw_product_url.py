# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-01-25 00:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_api', '0024_merge_20180115_1939'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='raw_product_url',
            field=models.CharField(blank=True, max_length=2000, null=True),
        ),
    ]
