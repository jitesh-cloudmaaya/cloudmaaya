# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-07 17:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_api', '0002_auto_20171030_2313'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='merchant_id',
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='product_id',
            field=models.BigIntegerField(blank=True, null=True),
        ),
    ]
