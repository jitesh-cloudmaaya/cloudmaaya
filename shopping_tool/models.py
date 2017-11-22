# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from product_api.models import Product


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
    wp_initiator_id = models.BigIntegerField()
    wp_target_id = models.BigIntegerField()
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
    stylist = models.ForeignKey(WpUsers, db_constraint=False, db_column='assigned_stylist_id', null=True, to_field='id', on_delete=models.DO_NOTHING)#models.BigIntegerField()
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

class Rack(models.Model):
    allume_styling_session = models.ForeignKey(AllumeStylingSessions, db_constraint=False, null=True, on_delete=models.DO_NOTHING)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
