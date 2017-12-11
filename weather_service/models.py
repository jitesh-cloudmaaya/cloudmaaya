# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Weather(models.Model):
    id = models.AutoField(primary_key=True) # added by Django by default?
    # id = models.BigAutoField(primary_key=True) # go with bigger?
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    # seeasonal attributes as value or label?
    spring_temperature = models.CharField(max_length=15, blank=True)
    spring_precipitation = models.CharField(max_length=15, blank=True)
    spring_snowfall = models.CharField(max_length=15, blank=True)
    spring_wind = models.CharField(max_length=15, blank=True)
    spring_sun = models.CharField(max_length=15, blank=True)

    summer_temperature = models.CharField(max_length=15, blank=True)
    summer_precipitation = models.CharField(max_length=15, blank=True)
    summer_snowfall = models.CharField(max_length=15, blank=True)
    summer_wind = models.CharField(max_length=15, blank=True)
    summer_sun = models.CharField(max_length=15, blank=True)

    autumn_temperature = models.CharField(max_length=15, blank=True)
    autumn_precipitation = models.CharField(max_length=15, blank=True)
    autumn_snowfall = models.CharField(max_length=15, blank=True)
    autumn_wind = models.CharField(max_length=15, blank=True)
    autumn_sun = models.CharField(max_length=15, blank=True)

    winter_temperature = models.CharField(max_length=15, blank=True)
    winter_precipitation = models.CharField(max_length=15, blank=True)
    winter_snowfall = models.CharField(max_length=15, blank=True)
    winter_wind = models.CharField(max_length=15, blank=True)
    winter_sun = models.CharField(max_length=15, blank=True)

    class Meta:
        db_table = 'weather_service' # should I add/specify a table?
        unique_together = (('city', 'state'),)

    # update create method with arguments to use in weather initialization
    @classmethod
    def create(cls):
        pass