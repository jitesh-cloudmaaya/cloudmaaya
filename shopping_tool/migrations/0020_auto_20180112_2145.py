# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-01-12 21:47
from __future__ import unicode_literals

from django.db import migrations, models
import sys
from catalogue_service.settings import DEBUG

class Migration(migrations.Migration):

    dependencies = [
        ('shopping_tool', '0019_allumelookproducts_allumelooks'),
    ]

    if 'test' in sys.argv or DEBUG:
        operations = [
            migrations.AddField(
                model_name='allumelookproducts',
                name='cropped_dimensions',
                field=models.CharField(blank=True, max_length=200, null=True),
            ),
            migrations.AddField(
                model_name='allumelookproducts',
                name='layout_position',
                field=models.IntegerField(default=0),
                preserve_default=False,
            ),
            migrations.AddField(
                model_name='allumelookproducts',
                name='raw_product_id',
                field=models.IntegerField(default=0),
            ),
            migrations.AddField(
                model_name='allumelooks',
                name='is_legacy',
                field=models.BooleanField(default=0),
            ),
            migrations.AddField(
                model_name='allumelooks',
                name='layout_id',
                field=models.IntegerField(default=0),
            ),
            migrations.AddIndex(
                model_name='allumelooks',
                index=models.Index(fields=['layout_id'], name='allume_look_layout__eed162_idx'),
            ),
            migrations.AddIndex(
                model_name='allumelookproducts',
                index=models.Index(fields=['raw_product_id'], name='allume_look_raw_pro_9d6dbb_idx'),
            ),
        ]
    else:
        operations = [
        ]