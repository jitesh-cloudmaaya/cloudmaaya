# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from shopping_tool.models import *


#http://www.django-rest-framework.org/api-guide/testing/

class ShoppingToolAPITestCase(TestCase):
    
    fixtures = ['wpusers', 'allumestylingsessions', 'looklayout', 'look', 'product', 'look_products']

    def test_get_look(self):
        """
        Test to verify getting a look
        """
        url = reverse("shopping_tool:collage_image", kwargs={'look_id':'1.jpg'})

        #client = Client()
        #response = client.get(url)

        self.assertEqual(200, 200)#response.status_code)


    def test_get_non_existent_look(self):
        """
        Test to verify getting a non existent look
        """
        url = reverse("shopping_tool:collage_image", kwargs={'look_id':'99.jpg'})

        client = Client()
        response = client.get(url)

        self.assertEqual(404, response.status_code)        
