# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.test import TestCase
from shopping_tool.models import Look, AllumeStylingSessions, WpUsers
from django.db import migrations, models

class LookTests(APITestCase):

    def setUp(self):

        print("Creating WP Users")
        migrations.CreateModel(
                    name='WpUsers',
                    fields=[
                        ('id', models.AutoField(db_column='ID', primary_key=True, serialize=False)),
                        ('user_login', models.CharField(max_length=60, unique=True)),
                        ('user_pass', models.CharField(max_length=255)),
                        ('user_nicename', models.CharField(blank=True, max_length=50, null=True)),
                        ('user_email', models.CharField(max_length=100, unique=True)),
                        ('user_url', models.CharField(blank=True, max_length=100, null=True)),
                        ('user_registered', models.DateTimeField(blank=True, null=True)),
                        ('user_activation_key', models.CharField(blank=True, max_length=255, null=True)),
                        ('user_status', models.IntegerField(blank=True, null=True)),
                        ('display_name', models.CharField(blank=True, max_length=250, null=True)),
                        ('first_name', models.CharField(blank=True, max_length=255, null=True)),
                        ('last_name', models.CharField(blank=True, max_length=255, null=True)),
                        ('user_phone', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                        ('notes', models.TextField(blank=True, null=True)),
                        ('timezone', models.CharField(blank=True, max_length=50, null=True)),
                        ('last_modified', models.DateTimeField(blank=True, null=True)),
                        ('last_login', models.DateTimeField(blank=True, null=True)),
                        ('is_superuser', models.IntegerField()),
                        ('is_staff', models.IntegerField()),
                        ('is_active', models.IntegerField()),
                        ('system_generated', models.TextField()),
                    ],
            options={
                'db_table': 'wp_users',
            },
        )

        print("Done Creating WP Users")

        #WpUsers.objects.create(user_email= "shopper@allume.co")
        #WpUsers.objects.create(user_email= "client@allume.co")
        AllumeStylingSessions.objects.create(name="Test Styling Session", shopper=1, client=1)

       

    def test_create_account(self):
        """
        Ensure we can create a new account object.
        """
        url = reverse('account-list')
        data = {"name": "Test Look 5huck", "look_layout": 1, "allume_styling_session":1, "stylist": 1}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Look.objects.count(), 1)
        self.assertEqual(Look.objects.get().name, 'Test Look 5huck')

