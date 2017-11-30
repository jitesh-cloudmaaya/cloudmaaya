# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from django.core.urlresolvers import reverse

from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from shopping_tool.models import Look, AllumeStylingSessions, WpUsers, Rack, LookLayout
from product_api.models import Product
from django.http.cookie import SimpleCookie

#http://www.django-rest-framework.org/api-guide/testing/

class ShoppingToolAPITestCase(APITestCase):
    
    fixtures = ['allumestylingsessions', 'looklayout', 'look', 'product']
    shopper = ''
    client = ''

    def setUp(self):        
        client = WpUsers.objects.create(user_email= "client@allume.co", user_phone=2, user_login='test2', is_superuser=1, is_staff=1, is_active=1, system_generated="No")
        self.client.cookies = SimpleCookie({'user_email': 'client@allume.co'})


    def test_create_look(self):
        """
        Test to verify creating a look
        """
        url = reverse("shopping_tool_api:look", kwargs={'pk':0})
        
        shopper = WpUsers.objects.create(user_email= "shopper@allume.co", user_phone=1, user_login='test1', is_superuser=1, is_staff=1, is_active=1, system_generated="No")
        data = {"name": "Api Test Look", "look_layout": 1, "allume_styling_session": 1, "stylist": shopper.id}

        response = self.client.put(url, data)
        response_data = json.loads(response.content)


        self.assertEqual(201, response.status_code)
        self.assertEqual(Look.objects.count(), 3)
        self.assertEqual(Look.objects.get(id = response_data['id']).name, 'Api Test Look')
        self.assertEqual(Look.objects.get(id = response_data['id']).look_layout.name, '5 Item Outfit')
        

    def test_update_look(self):
        """
        Test to verify updating a look
        """
        url = reverse("shopping_tool_api:look", kwargs={'pk':2})

        look_layout_instance = LookLayout.objects.get(id=1)
        shopper = WpUsers.objects.create(user_email= "shopper@allume.co", user_phone=1, user_login='test1', is_superuser=1, is_staff=1, is_active=1, system_generated="No")
        
        data = {"id": 2, "name": "Api Test Update Look", "look_layout": look_layout_instance, "allume_styling_session": 1, "stylist": shopper.id}

        #Verify the Original Look Name is in Place
        self.assertEqual(Look.objects.get(id = 2).name, 'Fixture Test Look 2')

        response = self.client.put(url, data)
        response_data = json.loads(response.content)


        self.assertEqual(201, response.status_code)
        self.assertEqual(Look.objects.count(), 2)
        self.assertEqual(Look.objects.get(id = 2).name, 'Api Test Update Look')


    def test_get_look(self):
        """
        Test to verify getting a look
        """
        url = reverse("shopping_tool_api:look", kwargs={'pk':1})

        response = self.client.get(url)
        response_data = json.loads(response.content)

        self.assertEqual(Look.objects.get(id = 1).name, response_data['name'])
        self.assertEqual(200, response.status_code)

    def test_add_rack_item(self):
        """
        Test to verify adding a product to a rack
        """
        url = reverse("shopping_tool_api:rack_item", kwargs={'pk':0})

        data = {"product": 1, "allume_styling_session": 3}
        response = self.client.put(url, data)

        self.assertEqual(201, response.status_code)
        self.assertEqual(Rack.objects.count(), 1)


    def test_delete_rack_item(self):
        """
        Test to verify deleting a product from a rack
        """
        session_instance = AllumeStylingSessions.objects.get(id =3)
        product_instance = Product.objects.get(id=1)

        # Have to create an object in order to delete it
        rack_instance = Rack.objects.create(product=product_instance, allume_styling_session=session_instance)

        url = reverse("shopping_tool_api:rack_item", kwargs={'pk':rack_instance.id})
        response = self.client.delete(url)

        self.assertEqual(201, response.status_code)
        self.assertEqual(Rack.objects.count(), 0)


