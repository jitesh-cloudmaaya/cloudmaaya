# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-10-19 07:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_api', '0053_auto_20180929_0656'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_final_sale',
            field=models.BooleanField(default=0),
        ),
    ]
