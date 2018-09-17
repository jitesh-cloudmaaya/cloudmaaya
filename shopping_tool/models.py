# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import yaml
import re

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from product_api.models import Product
import uuid
from django.utils.html import escape

from catalogue_service.settings_local import COLLAGE_IMAGE_ROOT

from django.utils import timezone

<<<<<<< HEAD
from django.contrib.auth.models import AbstractUser, BaseUserManager
=======
from django.contrib.auth.models import AbstractUser
>>>>>>> 09909669f33c3392509e59c85d3972a6afeeaeeb

# Create your models here.
# class StylistManager(models.Manager):
class StylistManager(BaseUserManager):
    def stylists(self):
        return self.filter(allumewpuserstylingroles__styling_role__in = ['stylist', 'coordinator']).filter(is_active = 1)
<<<<<<< HEAD
    # # using wp_user table for Django admin
    def get_by_natural_key(self, username):
        return self.get(username=username)
    def create_user(self, username, email, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            username=username,
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            username = username,
            email=email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

# class WpUser(models.Model):
#     id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
#     user_login = models.CharField(unique=True, max_length=60)
#     user_pass = models.CharField(max_length=255)
#     user_nicename = models.CharField(max_length=50, blank=True, null=True)
#     user_email = models.CharField(unique=True, max_length=100)
#     user_url = models.CharField(max_length=100, blank=True, null=True)
#     user_registered = models.DateTimeField(blank=True, null=True)
#     user_activation_key = models.CharField(max_length=255, blank=True, null=True)
#     user_status = models.IntegerField(blank=True, null=True)
#     display_name = models.CharField(max_length=250, blank=True, null=True)
#     first_name = models.CharField(max_length=255, blank=True, null=True)
#     last_name = models.CharField(max_length=255, blank=True, null=True)
#     user_phone = models.CharField(unique=True, max_length=100, blank=True, null=True)
#     notes = models.TextField(blank=True, null=True)
#     timezone = models.CharField(max_length=50, blank=True, null=True)
#     last_modified = models.DateTimeField(blank=True, null=True)
#     last_login = models.DateTimeField(blank=True, null=True)
#     is_superuser = models.IntegerField()
#     is_staff = models.IntegerField()
#     is_active = models.IntegerField()
#     system_generated = models.TextField()  # This field type is a guess.

#     class Meta:
#         managed = False
#         db_table = 'wp_users'

#     # added for stylist management system to show the stylist name in admin
#     def __unicode__(self):
#         return self.first_name + ' ' + self.last_name + ' (' + str(self.id) + ')'

#     objects = StylistManager()

#     def clean_client_360(self):
#         clean_client = self.client_360.__dict__

#         for k, v in clean_client.items():
#             clean_client[k] = escape(v).replace("\n", "").replace("\r", "")

#         return clean_client

#############################################
# Works in Progress (using WpUser as User)
#############################################

class WpUser(AbstractUser):
    id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID', db_column='ID')
    password = models.CharField(max_length=128, verbose_name='password', db_column='user_pass')
    last_login = models.DateTimeField(blank=True, null=True, verbose_name='last login')
    is_superuser = models.BooleanField(default=False,verbose_name='superuser status')
    username = models.CharField(error_messages={'unique': 'A user with that username already exists.'},
                                    max_length=150, unique=True,
                                    verbose_name='username', db_column= 'user_login')
    first_name = models.CharField(blank=True, max_length=30, verbose_name='first name')
    last_name = models.CharField(blank=True, max_length=30, verbose_name='last name')
    email = models.EmailField(blank=True, max_length=254, verbose_name='email address', db_column='user_email')
    phone = models.CharField(blank=True, null=True, max_length=254, verbose_name='user phone', db_column='user_phone')
    is_staff = models.BooleanField(default=False, verbose_name='staff status')
    is_active = models.BooleanField(default=True, verbose_name='active')
    date_joined = models.DateTimeField(verbose_name='date joined', db_column='user_registered')
    groups = models.ManyToManyField(blank=True,
                                        related_name='user_set', related_query_name='user', to='auth.Group',
                                        verbose_name='groups')
    user_permissions = models.ManyToManyField(blank=True, related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')
=======
    # # # using wp_user table for Django admin
    # def get_by_natural_key(self, username):
    #     return self.get(username=username)
    # def create_user(self, username, email, password=None):
    #     """
    #     Creates and saves a User with the given email, date of
    #     birth and password.
    #     """
    #     if not email:
    #         raise ValueError('Users must have an email address')

    #     user = self.model(
    #         username=username,
    #         email=self.normalize_email(email),
    #     )

    #     user.set_password(password)
    #     user.save(using=self._db)
    #     return user

    # def create_superuser(self, username, email, password):
    #     """
    #     Creates and saves a superuser with the given email, date of
    #     birth and password.
    #     """
    #     user = self.create_user(
    #         username = username,
    #         email=email,
    #         password=password,
    #     )
    #     user.is_admin = True
    #     user.save(using=self._db)
    #     return user

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
>>>>>>> 09909669f33c3392509e59c85d3972a6afeeaeeb

    class Meta:
        managed = False
        db_table = 'wp_users'

    # added for stylist management system to show the stylist name in admin
    def __unicode__(self):
        return self.first_name + ' ' + self.last_name + ' (' + str(self.id) + ')'

    objects = StylistManager()

    def clean_client_360(self):
        clean_client = self.client_360.__dict__

        for k, v in clean_client.items():
            clean_client[k] = escape(v).replace("\n", "").replace("\r", "")

        return clean_client

#############################################
# Works in Progress (using WpUser as User)
#############################################

# class WpUsers(AbstractUser):
#     id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID', db_column='ID')
#     password = models.CharField(max_length=128, verbose_name='password', db_column='user_pass')
#     last_login = models.DateTimeField(blank=True, null=True, verbose_name='last login')
#     is_superuser = models.BooleanField(default=False,verbose_name='superuser status')
#     username = models.CharField(error_messages={'unique': 'A user with that username already exists.'},
#                                     max_length=150, unique=True,
#                                     verbose_name='username', db_column= 'user_login')
#     first_name = models.CharField(blank=True, max_length=30, verbose_name='first name')
#     last_name = models.CharField(blank=True, max_length=30, verbose_name='last name')
#     email = models.EmailField(blank=True, max_length=254, verbose_name='email address', db_column='user_email')
#     phone = models.CharField(blank=True, null=True, max_length=254, verbose_name='user phone', db_column='user_phone')
#     is_staff = models.BooleanField(default=False, verbose_name='staff status')
#     is_active = models.BooleanField(default=True, verbose_name='active')
#     date_joined = models.DateTimeField(verbose_name='date joined', db_column='user_registered')
#     # groups = models.ManyToManyField(blank=True,
#     #                                     related_name='user_set', related_query_name='user', to='auth.Group',
#     #                                     verbose_name='groups')
#     # user_permissions = models.ManyToManyField(blank=True, related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')

#     class Meta:
#         managed = False
#         db_table = 'wp_users'

#     # added for stylist management system to show the stylist name in admin
#     def __unicode__(self):
#         return self.first_name + ' ' + self.last_name + ' (' + str(self.id) + ')'

#     objects = StylistManager()

#     def clean_client_360(self):
#         clean_client = self.client_360.__dict__

#         for k, v in clean_client.items():
#             clean_client[k] = escape(v).replace("\n", "").replace("\r", "")

#         return clean_client


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


class AllumeClient360(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    client = models.OneToOneField(WpUser, related_name='client_360', db_constraint=False, db_column='wp_user_id', null=True, to_field='id', on_delete=models.DO_NOTHING) #models.BigIntegerField() #Shopper
    first_name = models.TextField(blank=True, null=True)
    last_name = models.TextField(blank=True, null=True)
    address_1 = models.TextField(blank=True, null=True)
    address_2 = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    country = models.TextField(blank=True, null=True)
    birthday = models.TextField(blank=True, null=True)
    occupation = models.TextField(blank=True, null=True)
    wear_to_work = models.TextField(blank=True, null=True)
    spend_free_time = models.TextField(blank=True, null=True)
    where_live = models.TextField(blank=True, null=True)
    time_of_day_text = models.TextField(blank=True, null=True)
    social_media = models.TextField(blank=True, null=True)
    instagram = models.TextField(blank=True, null=True)
    pinterest = models.TextField(blank=True, null=True)
    linkedin = models.TextField(blank=True, null=True)
    photo = models.TextField(blank=True, null=True)
    winter = models.TextField(blank=True, null=True)
    spring = models.TextField(blank=True, null=True)
    summer = models.TextField(blank=True, null=True)
    fall = models.TextField(blank=True, null=True)
    styling_count = models.IntegerField(blank=True, null=True)
    last_styling_date = models.DateTimeField(blank=True, null=True)
    order_count = models.IntegerField(blank=True, null=True)
    last_order_amt = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    last_order_date = models.DateTimeField(blank=True, null=True)
    avg_items = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    avg_amt = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    heart_count = models.IntegerField(blank=True, null=True)
    comment_count = models.IntegerField(blank=True, null=True)
    star_count = models.IntegerField(blank=True, null=True)
    signup_date = models.DateTimeField(blank=True, null=True)
    utm_source = models.TextField(blank=True, null=True)
    utm_campaign = models.TextField(blank=True, null=True)
    utm_term = models.TextField(blank=True, null=True)
    utm_medium = models.TextField(blank=True, null=True)
    referral_site = models.TextField(blank=True, null=True)
    hear_about_allume = models.TextField(blank=True, null=True)
    height = models.TextField(blank=True, null=True)
    weight = models.TextField(blank=True, null=True)
    bra_size = models.TextField(blank=True, null=True)
    body_part_attention = models.TextField(blank=True, null=True)
    body_part_conceal = models.TextField(blank=True, null=True)
    fit_challenges = models.TextField(blank=True, null=True)
    hair_complex_color = models.TextField(blank=True, null=True)
    first_session_focus = models.TextField(blank=True, null=True)
    looks_goal = models.TextField(blank=True, null=True)
    pieces_focus = models.TextField(blank=True, null=True)
    outfits_preference = models.TextField(blank=True, null=True)
    other_goals = models.TextField(blank=True, null=True)
    stores = models.TextField(blank=True, null=True)
    brands = models.TextField(blank=True, null=True)
    spending_tops = models.TextField(blank=True, null=True)
    spending_bottoms = models.TextField(blank=True, null=True)
    spending_dresses = models.TextField(blank=True, null=True)
    spending_jackets = models.TextField(blank=True, null=True)
    spending_shoes = models.TextField(blank=True, null=True)
    style_celebs = models.TextField(blank=True, null=True, db_column='style_celebs')
    style_looks = models.TextField(blank=True, null=True, db_column='style_looks')
    style_jeans = models.TextField(blank=True, null=True, db_column='style_jeans')
    style_tops = models.TextField(blank=True, null=True, db_column='style_tops')
    style_dress = models.TextField(blank=True, null=True, db_column='style_dress')
    style_jacket = models.TextField(blank=True, null=True, db_column='style_jacket')
    style_shoe = models.TextField(blank=True, null=True, db_column='style_shoe')
    style_avoid = models.TextField(blank=True, null=True, db_column='style_avoid')
    colors_preference = models.TextField(blank=True, null=True)
    size_pants = models.TextField(blank=True, null=True)
    size_jeans = models.TextField(blank=True, null=True)
    size_tops = models.TextField(blank=True, null=True)
    size_shoe = models.TextField(blank=True, null=True)
    ears_pierced = models.TextField(blank=True, null=True)
    jewelry_style = models.TextField(blank=True, null=True)
    jewelry_type = models.TextField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'allume_client_360'


    # regex (will match until the } and leave it off)
    # ^([^}]+)
    @property
    def where_live_city(self):
        try:
            # trim potentially duplicate
            regex = '^([^}]+)'
            shortened = re.search(regex, self.where_live).group(0)
            shortened += '}'

            json_string = shortened
            obj = json.loads(json_string)
            return obj['city']
        except:
            return ''

    @property
    def where_live_state(self):
        try:
            # trim potentially duplicate
            regex = '^([^}]+)'
            shortened = re.search(regex, self.where_live).group(0)
            shortened += '}'

            json_string = shortened
            obj = json.loads(json_string)
            return obj['state']
        except:
            return ''




class AllumeQuizAnswerItems(models.Model):
    id = models.BigAutoField(primary_key=True)
    edit_version = models.BigIntegerField()
    quiz_id = models.BigIntegerField()
    quiz_question_answer = models.ForeignKey('AllumeQuizQuestionAnswers', models.DO_NOTHING)
    type = models.CharField(max_length=9)
    label = models.TextField(blank=True, null=True)
    value = models.CharField(max_length=255)
    s_order = models.IntegerField()
    s_order_old = models.IntegerField(blank=True, null=True)
    visible = models.TextField()  # This field type is a guess.
    date_created = models.DateTimeField()
    last_modified = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'allume_quiz_answer_items'


class AllumeQuizAuthor(models.Model):
    id = models.BigAutoField(primary_key=True)
    author_email = models.CharField(max_length=255)
    quiz = models.ForeignKey('AllumeQuizzes', models.DO_NOTHING)
    edit_version = models.BigIntegerField()
    date_created = models.DateTimeField()
    last_modified = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'allume_quiz_author'
        unique_together = (('quiz', 'edit_version'),)


class AllumeQuizImages(models.Model):
    id = models.BigAutoField(primary_key=True)
    author_email = models.CharField(max_length=255)
    url = models.CharField(unique=True, max_length=255)
    date_created = models.DateTimeField()
    last_modified = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'allume_quiz_images'


class AllumeQuizQuestionAnswers(models.Model):
    id = models.BigAutoField(primary_key=True)
    edit_version = models.BigIntegerField()
    quiz = models.ForeignKey('AllumeQuizzes', models.DO_NOTHING)
    question = models.TextField()
    name = models.CharField(max_length=255)
    js_widget_name = models.CharField(max_length=255, blank=True, null=True)
    quiz_step = models.ForeignKey('AllumeQuizSteps', models.DO_NOTHING)
    user_answer_max_choice = models.IntegerField(blank=True, null=True)
    choice_type = models.CharField(max_length=12)
    required = models.TextField()  # This field type is a guess.
    s_order = models.IntegerField()
    visible = models.TextField()  # This field type is a guess.
    date_created = models.DateTimeField()
    last_modified = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'allume_quiz_question_answers'
        unique_together = (('quiz', 'name'),)


class AllumeQuizStepGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    edit_version = models.BigIntegerField()
    name = models.CharField(max_length=255)
    quiz = models.ForeignKey('AllumeQuizzes', models.DO_NOTHING)
    step_group_trigger = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)
    visible = models.TextField()  # This field type is a guess.
    date_created = models.DateTimeField()
    last_modified = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'allume_quiz_step_groups'
        unique_together = (('quiz', 'name'),)


class AllumeQuizSteps(models.Model):
    id = models.BigAutoField(primary_key=True)
    edit_version = models.BigIntegerField()
    name = models.CharField(max_length=255)
    quiz = models.ForeignKey('AllumeQuizzes', models.DO_NOTHING)
    step_trigger = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)
    step_trigger_value = models.IntegerField(blank=True, null=True)
    step_value_formula = models.TextField(blank=True, null=True)
    step_group_id = models.BigIntegerField()
    visible = models.TextField()  # This field type is a guess.
    date_created = models.DateTimeField()
    last_modified = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'allume_quiz_steps'
        unique_together = (('quiz', 'name'),)


class AllumeQuizUserAnswers(models.Model):
    id = models.BigAutoField(primary_key=True)
    visitor_id = models.BigIntegerField()
    user = models.ForeignKey('AllumeClients', to_field='id') #, models.DO_NOTHING) #models.BigIntegerField(blank=True, null=True)
    user_email = models.CharField(max_length=255)
    quiz = models.ForeignKey('AllumeQuizzes', models.DO_NOTHING)
    quiz_version = models.BigIntegerField()
    quiz_question_answer = models.ForeignKey('AllumeQuizQuestionAnswers', models.DO_NOTHING)
    quiz_answer_item_ids = models.TextField()
    quiz_free_form_answer = models.TextField(blank=True, null=True)
    visible = models.TextField()  # This field type is a guess.
    date_created = models.DateTimeField()
    last_modified = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'allume_quiz_user_answers'
        unique_together = (('user_email', 'visitor_id', 'quiz_question_answer'),)


class AllumeQuizzes(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=255)
    edit_version = models.BigIntegerField()
    visible = models.TextField()  # This field type is a guess.
    date_created = models.DateTimeField()
    last_modified = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'allume_quizzes'


class AllumeStylingSessions(models.Model):
    id = models.BigAutoField(primary_key=True)
    token = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    client = models.ForeignKey(WpUser, related_name='client_user', db_constraint=False, db_column='wp_initiator_id', null=True, to_field='id', on_delete=models.DO_NOTHING) #models.BigIntegerField() #Client
    shopper = models.ForeignKey(WpUser, related_name='shopper_user', db_constraint=False, db_column='wp_target_id', null=True, to_field='id', on_delete=models.DO_NOTHING) #models.BigIntegerField() #Shopper
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    date_created = models.DateTimeField()
    last_modified = models.DateTimeField()
    revised_session_id = models.BigIntegerField(blank=True, null=True)
    stylist_assignment = models.ForeignKey('AllumeStylistAssignments', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'allume_styling_sessions'


class AllumeStylistAssignmentTypes(models.Model):
    id = models.BigAutoField(primary_key=True)
    stylist_assignment_type = models.CharField(unique=True, max_length=34)
    visible = models.TextField()  # This field type is a guess.
    s_order = models.IntegerField()
    duration_in_min = models.IntegerField()
    group_minute_diff_from_origin = models.IntegerField()
    calendar_color = models.CharField(max_length=50)
    stylist_entered_availability = models.TextField(blank=True, null=True)  # This field type is a guess.
    meeting_scheduled_with_client = models.TextField(blank=True, null=True)  # This field type is a guess.
    parent_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'allume_stylist_assignment_types'


class AllumeStylistAssignments(models.Model):
    id = models.BigAutoField(primary_key=True)
    assignment_author_id = models.BigIntegerField()
    stylist = models.ForeignKey(WpUser, db_constraint=False, db_column='assigned_stylist_id', null=True, to_field='id', on_delete=models.DO_NOTHING)#models.BigIntegerField()
    client = models.ForeignKey(AllumeClients, db_constraint=False, db_column='user_id', null=True, to_field='id', on_delete=models.DO_NOTHING) #models.BigIntegerField(blank=True, null=True)
    stylist_assignment_type = models.ForeignKey(AllumeStylistAssignmentTypes, models.DO_NOTHING)
    status = models.CharField(max_length=11)
    notes = models.TextField(blank=True, null=True)
    due_date = models.DateTimeField()
    date_created = models.DateTimeField()
    last_modified = models.DateTimeField()
    flexible = models.TextField()  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'allume_stylist_assignments'


class AllumeWpUserStylingRoles(models.Model):
    id = models.BigAutoField(primary_key=True)
    wp_stylist_id =  models.ForeignKey(WpUser, db_constraint=False, db_column='wp_stylist_id', null=True, to_field='id', on_delete=models.DO_NOTHING)#models.BigIntegerField(unique=True)
    styling_role = models.CharField(max_length=20)
    date_created = models.DateTimeField()
    last_modified = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'allume_wp_user_styling_roles'


class Rack(models.Model):
    allume_styling_session = models.ForeignKey(AllumeStylingSessions, db_constraint=False, null=True, on_delete=models.DO_NOTHING)
    product = models.ForeignKey(Product, db_constraint=False, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    stylist = models.ForeignKey(WpUser, db_constraint=False, null=True, to_field='id', on_delete=models.DO_NOTHING)

class AllumeLooks(models.Model):
    id = models.BigAutoField(primary_key=True)
    token = models.CharField(unique=True, max_length=50)
    allume_styling_session_id = models.BigIntegerField()
    wp_client_id = models.BigIntegerField()
    wp_stylist_id = models.BigIntegerField()
    name = models.CharField(max_length=100, blank=True, null=True)
    descrip = models.TextField(blank=True, null=True)
    collage = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=9)
    date_created = models.DateTimeField()
    # layout_id = models.IntegerField()
    last_modified = models.DateTimeField()
    is_legacy = models.IntegerField()
    position = models.IntegerField()
    # collage_image_data = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'allume_looks'
        # indexes = [
        #     models.Index(fields=['layout_id'])
        # ]



class AllumeLookProducts(models.Model):
    id = models.BigAutoField(primary_key=True)
    allume_look_id = models.BigIntegerField()
    wp_product_id = models.BigIntegerField()
    sequence = models.IntegerField()
    date_created = models.DateTimeField()
    last_modified = models.DateTimeField()
    product_clipped_stylist_id = models.BigIntegerField()
    cropped_dimensions = models.TextField(blank=True, null=True)
    layout_position = models.IntegerField()
    raw_product_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'allume_look_products'
        indexes = [
            models.Index(fields=['raw_product_id'])
        ]

class LookLayout(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    display_name = models.CharField(max_length=50, blank=True, null=True)
    _layout_json = models.TextField(blank=True, null=True, db_column="layout_json")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name

    @property
    def layout_json(self):
        return json.loads(self._layout_json)

    @property
    def layout_json_html(self):
        return json.dumps(json.loads(self._layout_json))

class Look(models.Model):
    #id = models.BigAutoField(primary_key=True)
    token = models.CharField(unique=True, max_length=50, default=uuid.uuid4)
    allume_styling_session = models.ForeignKey(AllumeStylingSessions, db_constraint=False, null=True, on_delete=models.DO_NOTHING)
    wp_client_id = models.BigIntegerField(blank=True, null=True, default =1 )
    stylist = models.ForeignKey(WpUser, db_constraint=False, db_column='wp_stylist_id', null=True, to_field='id', on_delete=models.DO_NOTHING)#models.BigIntegerField()
    name = models.CharField(max_length=100, blank=True)
    description = models.CharField(max_length=1000, blank=True, null=True, db_column='descrip')
    collage = models.TextField(blank=True, null=True, db_column='collage')
    status = models.CharField(max_length=11, default='Draft')
    created_at = models.DateTimeField(auto_now_add=True, null=True, db_column='date_created')
    updated_at = models.DateTimeField(auto_now=True, null=True, db_column='last_modified')
    is_legacy = models.IntegerField(blank=True, null=True, default = 0)
    # look_layout = models.ForeignKey(LookLayout, db_column='layout_id')
    look_products = models.ManyToManyField(Product, db_column='product_id', through='LookProduct')
    position = models.IntegerField(default=100)
    # collage_image_data = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-updated_at']
        managed = False
        db_table = 'allume_looks'
        
    def __str__(self):
        return self.name

class LookProduct(models.Model):
    look = models.ForeignKey(Look, related_name='product_set', db_constraint=False, db_column='allume_look_id')
    wp_product_id = models.BigIntegerField(blank=True, null=True, default=-1, db_column='wp_product_id')
    created_at = models.DateTimeField(auto_now_add=True, null=True, db_column='date_created')
    updated_at = models.DateTimeField(auto_now=True, null=True, db_column='last_modified')
    product_clipped_stylist_id = models.BigIntegerField(blank=True, null=True, default=-1)
    cropped_dimensions = models.CharField(max_length=2000, blank=True, null=True)
    layout_position = models.IntegerField(db_column='sequence')
    product = models.ForeignKey(Product, db_constraint=False, db_column='raw_product_id')
    in_collage = models.BooleanField(default=True)
    cropped_image_code = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'allume_look_products'

class UserProductFavorite(models.Model):
    stylist = models.ForeignKey(WpUser, db_constraint=False, db_column='assigned_stylist_id', null=True, to_field='id', on_delete=models.DO_NOTHING)#models.BigIntegerField()
    product = models.ForeignKey(Product, db_constraint=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    

class UserLookFavorite(models.Model):
    stylist = models.ForeignKey(WpUser, db_constraint=False, db_column='assigned_stylist_id', null=True, to_field='id', on_delete=models.DO_NOTHING)#models.BigIntegerField()
    look = models.ForeignKey(Look, db_constraint=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

class LookMetrics(models.Model):
    look = models.ForeignKey(Look, related_name='metric_set', db_constraint=False, db_column='allume_look_id')
    average_item_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_look_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_favorites = models.IntegerField()
    total_item_sales = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True) #Blank for now
    store_rank = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True) #Blank for now  

class AllumeUserStylistNotes(models.Model):
    id = models.BigAutoField(primary_key=True)
    stylist = models.ForeignKey(WpUser, db_constraint=False, db_column='last_author_id', null=True, to_field='id', on_delete=models.DO_NOTHING)#models.BigIntegerField()
    client = models.ForeignKey(WpUser, related_name='client_id', db_constraint=False, db_column='user_id', null=True, to_field='id', on_delete=models.DO_NOTHING) #models.BigIntegerField() #Client
    notes = models.TextField()
    styling_session = models.ForeignKey(AllumeStylingSessions, db_column='styling_session_id', db_constraint=False, null=True, on_delete=models.DO_NOTHING)
    visible = models.IntegerField()
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    last_modified = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        managed = False
        db_table = 'allume_user_stylist_notes'

class StyleType(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    looks = models.ManyToManyField(Look, db_constraint=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Style Types"

class StyleOccasion(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    looks = models.ManyToManyField(Look, db_constraint=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Style Occasions"

@receiver(pre_save, sender=Look)
def set_look_client_id(sender, instance, *args, **kwargs):
    instance.wp_client_id = instance.allume_styling_session.client.id
    #instance.collage = "%s/%s.jpg" % (COLLAGE_IMAGE_ROOT, instance.id)

#@receiver(pre_save, sender=LookProduct)
#def set_product_clipped_stylist_id(sender, instance, *args, **kwargs):
#    instance.product_clipped_stylist_id = instance.look.stylist.id


# ---------------------------------
#   model for reporting
# ---------------------------------

class Report(models.Model):
    product_id = models.BigIntegerField()
    merchant_id = models.BigIntegerField()
    stylist_id = models.CharField(max_length=50)
    datetime = models.DateTimeField(default=timezone.now)
    source = models.CharField(max_length=50)
    anna_availability = models.CharField(max_length=20)
    reason = models.CharField(max_length=50)