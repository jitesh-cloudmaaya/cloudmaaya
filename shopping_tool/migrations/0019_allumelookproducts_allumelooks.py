# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-01-12 20:58
from __future__ import unicode_literals

from django.db import migrations, models
import sys
from catalogue_service.settings import DEBUG

class Migration(migrations.Migration):

    dependencies = [
        ('shopping_tool', '0018_auto_20171221_1747'),
    ]

    if 'test' in sys.argv or DEBUG:
        operations = [
            migrations.CreateModel(
                name='AllumeLookProducts',
                fields=[
                    ('id', models.BigAutoField(primary_key=True, serialize=False)),
                    ('allume_look_id', models.BigIntegerField()),
                    ('wp_product_id', models.BigIntegerField()),
                    ('sequence', models.IntegerField()),
                    ('date_created', models.DateTimeField()),
                    ('last_modified', models.DateTimeField()),
                    ('product_clipped_stylist_id', models.BigIntegerField()),
                ],
                options={
                    'db_table': 'allume_look_products',
                    'managed': True,
                },
            ),
            migrations.CreateModel(
                name='AllumeLooks',
                fields=[
                    ('id', models.BigAutoField(primary_key=True, serialize=False)),
                    ('token', models.CharField(max_length=50, unique=True)),
                    ('allume_styling_session_id', models.BigIntegerField()),
                    ('wp_client_id', models.BigIntegerField()),
                    ('wp_stylist_id', models.BigIntegerField()),
                    ('name', models.CharField(blank=True, max_length=100, null=True)),
                    ('descrip', models.TextField(blank=True, null=True)),
                    ('collage', models.CharField(blank=True, max_length=200, null=True)),
                    ('status', models.CharField(max_length=9)),
                    ('date_created', models.DateTimeField()),
                    ('last_modified', models.DateTimeField()),
                    ('position', models.IntegerField(default=100)),
                ],
                options={
                    'db_table': 'allume_looks',
                    'managed': True,
                },
            ),
        ]
    else:
        operations = [
        ]
