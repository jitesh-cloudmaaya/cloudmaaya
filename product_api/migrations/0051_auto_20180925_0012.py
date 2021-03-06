# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-09-25 00:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_api', '0050_auto_20180925_0011'),
    ]

    operations = [
        migrations.AddField(
            model_name='merchant',
            name='coupon_code',
            field=models.CharField(blank=True, default=None, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='merchant',
            name='coupon_description',
            field=models.CharField(blank=True, default=None, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='merchant',
            name='coupon_end_date',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='merchant',
            name='coupon_start_date',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='merchant',
            name='coupon_update_notes',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='merchant',
            name='order_via_twotap',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='merchant',
            name='order_via_twotap_use_client_email',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='merchant',
            name='return_policy',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='merchant',
            name='shipping_policy',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='merchant',
            name='show_generic_coupon_message',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='merchant',
            name='two_tap_supported',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='merchant',
            name='twotap_id',
            field=models.CharField(blank=True, default=None, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='merchant',
            name='url_host',
            field=models.CharField(blank=True, default=None, max_length=50, null=True),
        ),
    ]
