# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-12-14 21:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weather_service', '0002_auto_20171212_0028'),
    ]

    operations = [
        migrations.AddField(
            model_name='weather',
            name='autumn_description',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='weather',
            name='autumn_icon',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='weather',
            name='spring_description',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='weather',
            name='spring_icon',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='weather',
            name='summer_description',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='weather',
            name='summer_icon',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='weather',
            name='winter_description',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='weather',
            name='winter_icon',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]
