# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-09-25 19:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('stylist_management', '0002_auto_20180919_1814'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stylistprofile',
            name='start_date',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True),
        ),
    ]
