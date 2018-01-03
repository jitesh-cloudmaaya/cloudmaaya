# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-01-03 18:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product_api', '0018_allumecategory'),
    ]

    operations = [
        migrations.AddField(
            model_name='categorymap',
            name='allume_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='product_api.AllumeCategory'),
        ),
    ]
