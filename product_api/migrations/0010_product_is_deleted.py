# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-12 07:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_api', '0009_initial_merchant_categories_20171107_2355'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_deleted',
            field=models.BooleanField(default=0),
        ),
    ]
