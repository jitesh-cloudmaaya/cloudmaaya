# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.test import TestCase
from shopping_tool.models import Look, AllumeStylingSessions, WpUsers

class LookTests(APITestCase):

    def setUp(self):
    	print "Starting Setup"
    	WpUsers.objects.create(user_email= "shopper@allume.co")
    	WpUsers.objects.create(user_email= "client@allume.co")
        AllumeStylingSessions.objects.create(name="Test Styling Session", shopper=1, client=1)
        print "Ending Setup"
       

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

