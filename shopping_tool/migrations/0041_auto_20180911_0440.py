# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-09-11 04:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopping_tool', '0040_report'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='merchant_id',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='report',
            name='product_id',
            field=models.BigIntegerField(),
        ),
    ]
