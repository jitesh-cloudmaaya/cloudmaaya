# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-01-11 20:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopping_tool', '0017_auto_20180111_2001'),
    ]

    operations = [
        migrations.AlterField(
            model_name='look',
            name='status',
            field=models.CharField(default='Draft', max_length=11),
        ),
    ]
