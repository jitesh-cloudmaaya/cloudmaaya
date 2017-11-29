# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from django.core.urlresolvers import reverse

from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from shopping_tool.models import Look, AllumeStylingSessions, WpUsers


class ShoppingToolAPICreateAPIViewTestCase(APITestCase):
    
    fixtures = ['allumestylingsessions.yaml']

    def setUp(self):
        shopper = WpUsers.objects.create(user_email= "shopper@allume.co", user_phone=1, user_login='test1', is_superuser=1, is_staff=1, is_active=1, system_generated="No")
        client = WpUsers.objects.create(user_email= "client@allume.co", user_phone=2, user_login='test2', is_superuser=1, is_staff=1, is_active=1, system_generated="No")
        #AllumeStylingSessions.objects.create(name="Test Styling Session", shopper=shopper, client=client)


    def test_create_look(self):
        url = reverse("shopping_tool_api:look", kwargs={'pk':0})
        data = {"name": "Test Look 5huck", "look_layout": 1, "allume_styling_session": 1, "stylist": 1}
        response = self.client.put(url, data)

        expected_data = '{"id": 1, "name": "Test Look 5huck", "status": "Active", "created_at": "2017-11-29T19:34:14.679851Z", "updated_at": "2017-11-29T19:34:14.679945Z", "allume_styling_session": 1, "look_layout": 1, "stylist": 1, "look_products": []}'

        self.assertEqual(200, response.status_code)
        #self.assertEqual(str(expected_data), str(response.content))
        self.assertEqual(Look.objects.count(), 1)
        self.assertEqual(Look.objects.get().name, 'Test Look 5huck')

  #  def test_user_todos(self)
  ##      """
   #     Test to verify user todos list
  #      """
  #      Todo.objects.create(user=self.user, name="Clean the car!")
  #      response = self.client.get(self.url)
  #      self.assertTrue(len(json.loads(response.content)) == Todo.objects.count())



"""
class LookTests(TestCase):

    def setUp(self):


        shopper = WpUsers.objects.create(user_email= "shopper@allume.co", user_phone=1, user_login='test1', is_superuser=1, is_staff=1, is_active=1, system_generated="No")
        client = WpUsers.objects.create(user_email= "client@allume.co", user_phone=2, user_login='test2', is_superuser=1, is_staff=1, is_active=1, system_generated="No")
        #AllumeStylingSessions.objects.create(name="Test Styling Session", shopper=shopper, client=client)

       

    def test_create_account(self):

        factory = APIRequestFactory()
        

        data = {"name": "Test Look 5huck", "look_layout": 1, "allume_styling_session":1, "stylist": 1}

        request = factory.put('/shopping_tool_api/look/0/', data)
        print(dir(request))
        
       
        #response = self.client.put(url, data, format='json')
        #self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Look.objects.count(), 0)
        #self.assertEqual(Look.objects.get().name, 'Test Look 5huck')

"""