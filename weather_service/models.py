# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Weather(models.Model):


    # update create method with arguments to use in weather initialization
    def create(cls):
        pass