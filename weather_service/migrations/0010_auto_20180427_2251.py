# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-04-27 22:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weather_service', '0009_auto_20180427_2250'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weather',
            name='_autumn_precipitation',
            field=models.FloatField(db_column='autumn_precipitation', default=None, null=True),
        ),
        migrations.AlterField(
            model_name='weather',
            name='_autumn_snowfall',
            field=models.FloatField(db_column='autumn_snowfall', default=None, null=True),
        ),
        migrations.AlterField(
            model_name='weather',
            name='_autumn_sun',
            field=models.FloatField(db_column='autumn_sun', default=None, null=True),
        ),
        migrations.AlterField(
            model_name='weather',
            name='_autumn_temperature_average',
            field=models.FloatField(db_column='autumn_temperature_average', default=None, null=True),
        ),
        migrations.AlterField(
            model_name='weather',
            name='_autumn_temperature_high',
            field=models.FloatField(db_column='autumn_temperature_high', default=None, null=True),
        ),
        migrations.AlterField(
            model_name='weather',
            name='_autumn_temperature_low',
            field=models.FloatField(db_column='autumn_temperature_low', default=None, null=True),
        ),
        migrations.AlterField(
            model_name='weather',
            name='_autumn_wind',
            field=models.FloatField(db_column='autumn_wind', default=None, null=True),
        ),
        migrations.AlterField(
            model_name='weather',
            name='_spring_precipitation',
            field=models.FloatField(db_column='spring_precipitation', default=None, null=True),
        ),
        migrations.AlterField(
            model_name='weather',
            name='_spring_snowfall',
            field=models.FloatField(db_column='spring_snowfall', default=None, null=True),
        ),
        migrations.AlterField(
            model_name='weather',
            name='_spring_sun',
            field=models.FloatField(db_column='spring_sun', default=None, null=True),
        ),
        migrations.AlterField(
            model_name='weather',
            name='_spring_temperature_average',
            field=models.FloatField(db_column='spring_temperature_average', default=None, null=True),
        ),
        migrations.AlterField(
            model_name='weather',
            name='_spring_temperature_high',
            field=models.FloatField(db_column='spring_temperature_high', default=None, null=True),
        ),
        migrations.AlterField(
            model_name='weather',
            name='_spring_temperature_low',
            field=models.FloatField(db_column='spring_temperature_low', default=None, null=True),
        ),
        migrations.AlterField(
            model_name='weather',
            name='_spring_wind',
            field=models.FloatField(db_column='spring_wind', default=None, null=True),
        ),
        migrations.AlterField(
            model_name='weather',
            name='_summer_precipitation',
            field=models.FloatField(db_column='summer_precipitation', default=None, null=True),
        ),
        migrations.AlterField(
            model_name='weather',
            name='_summer_snowfall',
            field=models.FloatField(db_column='summer_snowfall', default=None, null=True),
        ),
        migrations.AlterField(
            model_name='weather',
            name='_summer_sun',
            field=models.FloatField(db_column='summer_sun', default=None, null=True),
        ),
        migrations.AlterField(
            model_name='weather',
            name='_summer_temperature_average',
            field=models.FloatField(db_column='summer_temperature_average', default=None, null=True),
        ),
        migrations.AlterField(
            model_name='weather',
            name='_summer_temperature_high',
            field=models.FloatField(db_column='summer_temperature_high', default=None, null=True),
        ),
        migrations.AlterField(
            model_name='weather',
            name='_summer_temperature_low',
            field=models.FloatField(db_column='summer_temperature_low', default=None, null=True),
        ),
        migrations.AlterField(
            model_name='weather',
            name='_summer_wind',
            field=models.FloatField(db_column='summer_wind', default=None, null=True),
        ),
        migrations.AlterField(
            model_name='weather',
            name='_winter_precipitation',
            field=models.FloatField(db_column='winter_precipitation', default=None, null=True),
        ),
        migrations.AlterField(
            model_name='weather',
            name='_winter_snowfall',
            field=models.FloatField(db_column='winter_snowfall', default=None, null=True),
        ),
        migrations.AlterField(
            model_name='weather',
            name='_winter_sun',
            field=models.FloatField(db_column='winter_sun', default=None, null=True),
        ),
        migrations.AlterField(
            model_name='weather',
            name='_winter_temperature_average',
            field=models.FloatField(db_column='winter_temperature_average', default=None, null=True),
        ),
        migrations.AlterField(
            model_name='weather',
            name='_winter_temperature_high',
            field=models.FloatField(db_column='winter_temperature_high', default=None, null=True),
        ),
        migrations.AlterField(
            model_name='weather',
            name='_winter_temperature_low',
            field=models.FloatField(db_column='winter_temperature_low', default=None, null=True),
        ),
        migrations.AlterField(
            model_name='weather',
            name='_winter_wind',
            field=models.FloatField(db_column='winter_wind', default=None, null=True),
        ),
    ]
