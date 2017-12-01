# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-09 05:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product_api', '0007_auto_20171108_0739'),
    ]

    operations = [
        migrations.CreateModel(
            name='MerchantCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_merchant_id', models.IntegerField(blank=True, null=True)),
                ('name', models.CharField(blank=True, max_length=128, null=True)),
                ('active', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
            ],
        ),
        migrations.RenameField(
            model_name='merchant',
            old_name='status',
            new_name='active',
        ),
        migrations.RenameField(
            model_name='merchant',
            old_name='merchant_name',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='network',
            old_name='status',
            new_name='active',
        ),
        migrations.RenameField(
            model_name='network',
            old_name='network_name',
            new_name='name',
        ),
        migrations.AddField(
            model_name='merchantcategory',
            name='network',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product_api.Network'),
        ),
    ]
