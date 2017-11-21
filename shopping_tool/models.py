# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class WpUsers(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    user_login = models.CharField(unique=True, max_length=60)
    user_pass = models.CharField(max_length=255)
    user_nicename = models.CharField(max_length=50, blank=True, null=True)
    user_email = models.CharField(unique=True, max_length=100)
    user_url = models.CharField(max_length=100, blank=True, null=True)
    user_registered = models.DateTimeField(blank=True, null=True)
    user_activation_key = models.CharField(max_length=255, blank=True, null=True)
    user_status = models.IntegerField(blank=True, null=True)
    display_name = models.CharField(max_length=250, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    user_phone = models.CharField(unique=True, max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    timezone = models.CharField(max_length=50, blank=True, null=True)
    last_modified = models.DateTimeField(blank=True, null=True)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    system_generated = models.TextField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'wp_users'


class AllumeClients(models.Model):
    id = models.BigAutoField(primary_key=True)
    wp_client_id = models.BigIntegerField(blank=True, null=True)
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)
    email = models.CharField(unique=True, max_length=80)
    phone = models.CharField(unique=True, max_length=100, blank=True, null=True)
    variant = models.CharField(max_length=30, blank=True, null=True)
    utm_source = models.CharField(max_length=80, blank=True, null=True)
    utm_medium = models.CharField(max_length=80, blank=True, null=True)
    utm_campaign = models.CharField(max_length=80, blank=True, null=True)
    survey_monkey_survey_id = models.CharField(max_length=20, blank=True, null=True)
    survey_monkey_collector_id = models.CharField(max_length=20, blank=True, null=True)
    survey_monkey_response_id = models.CharField(max_length=20, blank=True, null=True)
    quiz_url = models.CharField(max_length=200, blank=True, null=True)
    bottle_conversation_id = models.CharField(max_length=200, blank=True, null=True)
    descrip = models.TextField(blank=True, null=True)
    coordinator_notes = models.TextField(blank=True, null=True)
    learnings = models.TextField(blank=True, null=True)
    allume_status_id = models.BigIntegerField()
    wp_stylist_id = models.BigIntegerField()
    is_active = models.IntegerField()
    date_created = models.DateTimeField()
    last_modified = models.DateTimeField()
    utm_term = models.CharField(max_length=80, blank=True, null=True)
    styling_fee_status = models.CharField(max_length=21, blank=True, null=True)
    styling_fee_value = models.TextField(blank=True, null=True)
    old_phone = models.CharField(max_length=80, blank=True, null=True)
    active_in_dashboard = models.TextField()  # This field type is a guess.
    first_time_consultation_time_to_reach_out = models.DateTimeField(blank=True, null=True)
    timezone = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'allume_clients'