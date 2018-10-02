# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-09-25 00:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_api', '0049_auto_20180615_0011'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='allumeretailersizemapping',
            options={},
        ),
        migrations.RemoveIndex(
            model_name='product',
            name='product_api_merchan_a8f549_idx',
        ),
        migrations.RemoveField(
            model_name='categorymap',
            name='active',
        ),
        migrations.AddField(
            model_name='categorymap',
            name='turned_on',
            field=models.BooleanField(db_column='active', default=False),
        ),
        migrations.AlterField(
            model_name='merchant',
            name='search_rank',
            field=models.IntegerField(default=0),
        ),
    ]