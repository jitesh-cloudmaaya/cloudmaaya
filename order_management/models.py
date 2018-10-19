# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Order_Job(models.Model):

    ID = models.IntegerField(primary_key=True)
    status = models.CharField(max_length=50)
    reason = models.CharField(max_length=50)
    detail = models.CharField(max_length=255)
    clickable = models.URLField(max_length=255)
    allume_cart_id = models.BigIntegerField()
    date_created = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'iterative_checkout_order_job'
