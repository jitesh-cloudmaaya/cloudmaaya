# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from django.db import models
from product_api.models import Merchant

class ShippingPrice(models.Model):
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
    min_threshold = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    threshold = models.DecimalField(max_digits=15, decimal_places=2, default=1000000.00)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    location = models.CharField(max_length=3, default='US')
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    # added price range to show in admin
    def __unicode__(self):
        return "%s (%s) " % (self.merchant_id.name, self.amount)

# a proxy of Merchant class for full MerchantEditing
class MerchantEditing(Merchant): # proxy model to allow register same model twice
    class Meta:
        proxy=True