# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-01-03 18:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_api', '0013_auto_20180102_1953'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='availability',
        ),
        migrations.AddField(
            model_name='product',
            name='merchant_color',
            field=models.TextField(blank=True, max_length=255, null=True),
        ),
    ]
