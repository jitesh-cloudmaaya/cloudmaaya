# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-03-23 20:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_api', '0036_merge_20180305_1859'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categorymap',
            name='external_cat1',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='primary_category',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]