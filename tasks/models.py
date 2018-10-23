# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class ProductFeedLog(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    parentId = models.ForeignKey("ProductFeedLog", blank=True, null=True)
    step = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    result = models.CharField(max_length=2000, blank=True, null=True)
    start_time = models.DateTimeField(auto_now_add=True, null=True)
    end_time = models.DateTimeField(auto_now=True, null=True)

