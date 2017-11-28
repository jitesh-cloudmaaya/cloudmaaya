# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-21 21:02
from __future__ import unicode_literals

from django.db import migrations


from shopping_tool.models import LookLayout

def add_layouts(apps, schema_editor):
    LookLayout.objects.create(name="5 Item Outfit", display_name="5 Item Outfit", rows=5, columns=1, row_heights="20,20,20,20,20", column_widths="100")
    LookLayout.objects.create(name="3 Item Outfit", display_name="3 Item Outfit", rows=3, columns=1, row_heights="30,40,30", column_widths="100")
    

class Migration(migrations.Migration):

    dependencies = [
        ('shopping_tool', '0005_auto_20171125_0914'),
    ]

    operations = [
        migrations.RunPython(add_layouts)
    ]

