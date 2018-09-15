# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from django.db import models
from shopping_tool.models import WpUser

from auditlog.registry import auditlog # detail logging


# ---------------------------------
#   model for stylist profile
# ---------------------------------

class StylistRole(models.Model):

    role = models.CharField(max_length = 20, primary_key=True)
    class Meta:
        managed = True

    def __unicode__(self):
        return self.role

class ClientTier(models.Model):
    tier = models.IntegerField(primary_key=True)
    class Meta:
        managed = True

    def __unicode__(self):
        return str(self.tier)

class StylistProfile(models.Model):

    stylist = models.ForeignKey(WpUser, on_delete=models.CASCADE, unique=True)
    director = models.ForeignKey(WpUser, on_delete=models.SET_NULL, null=True, blank=True, related_name = 'director_r')
    manager = models.ForeignKey(WpUser, on_delete=models.SET_NULL, null=True, blank=True, related_name = 'manager_r')
    asm = models.ForeignKey(WpUser, on_delete=models.SET_NULL, null=True, blank=True, related_name = 'asm_r')
    role = models.ForeignKey(StylistRole, default='Stylist', on_delete=models.SET_NULL, null=True)
    on_duty = models.BooleanField(default=False)
    on_board = models.BooleanField(default=True)
    client_tier = models.ForeignKey(ClientTier, default=2, on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    off_board_date = models.DateField(null=True, blank=True)
    pay_rate = models.FloatField(null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)

# a proxy of StylistProfile class for StylistManagement
class StylistManagement(StylistProfile): # proxy model to allow register same model twice
    class Meta:
        proxy=True

# class StylistRoleRelation(models.Model):

#     role = models.ForeignKey(StylistRole , on_delete = models.CASCADE)
#     parent_role = models.ForeignKey(StylistRole, on_delete = models.CASCADE)


#######################
# Detail Logging
#######################
auditlog.register(StylistProfile)
auditlog.register(StylistManagement)
