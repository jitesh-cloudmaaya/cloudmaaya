# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-01-03 19:13
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product_api', '0020_remove_categorymap_allume_cat1'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='merchantcategory',
            name='allume_name',
        ),
    ]
