# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-01-05 20:20
from __future__ import unicode_literals

from django.db import migrations, models
from shopping_tool.models import *


def clean_up_old_layouts(apps, schema_editor):
    UserLookFavorite.objects.all().delete()
    LookProduct.objects.all().delete()
    Look.objects.all().delete()
    LookLayout.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('shopping_tool', '0015_auto_20171214_0531'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='looklayout',
            name='column_widths',
        ),
        migrations.RemoveField(
            model_name='looklayout',
            name='columns',
        ),
        migrations.RemoveField(
            model_name='looklayout',
            name='row_heights',
        ),
        migrations.RemoveField(
            model_name='looklayout',
            name='rows',
        ),
        migrations.AddField(
            model_name='looklayout',
            name='layout_json',
            field=models.TextField(blank=True, null=True),
        ),
        # line removed to prevent conflict with effects 0037-0039_auto_20180208_222x during localtests and circleCI
        migrations.RunPython(clean_up_old_layouts),
    ]
