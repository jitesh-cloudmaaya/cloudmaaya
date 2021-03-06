# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-12-12 00:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Weather',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('city', models.CharField(max_length=255)),
                ('state', models.CharField(max_length=255)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('spring_temperature', models.CharField(blank=True, max_length=15)),
                ('spring_precipitation', models.CharField(blank=True, max_length=15)),
                ('spring_snowfall', models.CharField(blank=True, max_length=15)),
                ('spring_wind', models.CharField(blank=True, max_length=15)),
                ('spring_sun', models.CharField(blank=True, max_length=15)),
                ('summer_temperature', models.CharField(blank=True, max_length=15)),
                ('summer_precipitation', models.CharField(blank=True, max_length=15)),
                ('summer_snowfall', models.CharField(blank=True, max_length=15)),
                ('summer_wind', models.CharField(blank=True, max_length=15)),
                ('summer_sun', models.CharField(blank=True, max_length=15)),
                ('autumn_temperature', models.CharField(blank=True, max_length=15)),
                ('autumn_precipitation', models.CharField(blank=True, max_length=15)),
                ('autumn_snowfall', models.CharField(blank=True, max_length=15)),
                ('autumn_wind', models.CharField(blank=True, max_length=15)),
                ('autumn_sun', models.CharField(blank=True, max_length=15)),
                ('winter_temperature', models.CharField(blank=True, max_length=15)),
                ('winter_precipitation', models.CharField(blank=True, max_length=15)),
                ('winter_snowfall', models.CharField(blank=True, max_length=15)),
                ('winter_wind', models.CharField(blank=True, max_length=15)),
                ('winter_sun', models.CharField(blank=True, max_length=15)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='weather',
            unique_together=set([('city', 'state')]),
        ),
    ]
