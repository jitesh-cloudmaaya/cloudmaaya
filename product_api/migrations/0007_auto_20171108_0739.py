# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-08 07:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_api', '0005_auto_20171108_0533'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='merchant_id',
            field=models.BigIntegerField(blank=True, db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='product_id',
            field=models.BigIntegerField(blank=True, db_index=True, null=True),
        ),
    ]
