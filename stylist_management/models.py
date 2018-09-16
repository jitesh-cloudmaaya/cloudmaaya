# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from django.db import models
from shopping_tool.models import WpUsers

from auditlog.registry import auditlog # detail logging

from django.db.models.signals import post_save # post save signal
from django.db import connection # to perform raw SQL query

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

    stylist = models.ForeignKey(WpUsers, on_delete=models.CASCADE, unique=True)
    director = models.ForeignKey(WpUsers, on_delete=models.SET_NULL, null=True, blank=True, related_name = 'director_r')
    manager = models.ForeignKey(WpUsers, on_delete=models.SET_NULL, null=True, blank=True, related_name = 'manager_r')
    asm = models.ForeignKey(WpUsers, on_delete=models.SET_NULL, null=True, blank=True, related_name = 'asm_r')
    role = models.ForeignKey(StylistRole, default='Stylist', on_delete=models.SET_NULL, null=True)
    on_duty = models.BooleanField(default=False)
    on_board = models.BooleanField(default=True)
    client_tier = models.ForeignKey(ClientTier, default=2, on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    off_board_date = models.DateTimeField(null=True, blank=True)
    pay_rate = models.FloatField(null=True, blank=True)
    birthday = models.DateTimeField(null=True, blank=True)

    # added for stylist management system to show the stylist name in admin
    def __unicode__(self):
        return str(self.stylist)

# a proxy of StylistProfile class for StylistManagement
class StylistManagement(StylistProfile): # proxy model to allow register same model twice
    class Meta:
        proxy=True

#--------------------------------------------------------------------
# post_save signal to update 'allume_wp_user_styling_roles' table
# everytime a StylistProfile or StylistManagement model is changed
#--------------------------------------------------------------------
def update_role(sender, instance, **kwargs):
    stylist_id = instance.stylist.id
    role = instance.role.role
    if sender == StylistProfile:
        if role!='Stylist':
            query_to_allume_wp_user_styling_roles(new_role='coordinator', stylist_id=stylist_id)
    elif sender == StylistManagement:
        if role=='Stylist':
            query_to_allume_wp_user_styling_roles(new_role='stylist', stylist_id=stylist_id)
    else:
        print('failed')

def query_to_allume_wp_user_styling_roles(new_role, stylist_id):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE allume_wp_user_styling_roles SET styling_role = %s WHERE wp_stylist_id=%s
            """
            , [new_role, stylist_id]
        )

post_save.connect(update_role, sender=StylistProfile)
post_save.connect(update_role, sender=StylistManagement)

# class StylistRoleRelation(models.Model):

#     role = models.ForeignKey(StylistRole , on_delete = models.CASCADE)
#     parent_role = models.ForeignKey(StylistRole, on_delete = models.CASCADE)


#######################
# Detail Logging
#######################
auditlog.register(StylistProfile)
auditlog.register(StylistManagement)
