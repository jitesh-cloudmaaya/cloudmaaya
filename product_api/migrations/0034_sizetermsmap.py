# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-02-27 22:40
from __future__ import unicode_literals

from django.db import migrations, models
import sys

class Migration(migrations.Migration):

    dependencies = [
        ('product_api', '0033_shoesizemap'),
    ]

    if 'test' in sys.argv:
        operations = [
            migrations.CreateModel(
                name='SizeTermsMap',
                fields=[
                    ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                    ('merchant_phrase', models.CharField(blank=True, max_length=128, null=True)),
                    ('allume_attribute', models.CharField(blank=True, max_length=128, null=True)),
                    ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                    ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ],
            ),
        ]
    else:
        operations = [
        ]
