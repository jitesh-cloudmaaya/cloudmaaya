# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from django.core.urlresolvers import reverse

from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from shopping_tool.models import *
from django.http.cookie import SimpleCookie

#http://www.django-rest-framework.org/api-guide/testing/

class ShoppingToolAPITestCase(APITestCase):
    
    fixtures = ['allumestylingsessions', 'looklayout', 'look', 'product', 'user_look_favorite', 'user_product_favorite', 'allume_client_360_test']
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
        self.assertEqual(Look.objects.count(), 4)
        self.assertEqual(Look.objects.get(id = response_data['id']).name, 'Api Test Look')
        self.assertEqual(Look.objects.get(id = response_data['id']).look_layout.name, 'one_item')
        

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
        self.assertEqual(Look.objects.count(), 3)
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

    def test_get_rack_item(self):
        """
        Test to verify getting a product from a rack
        """

        session_instance = AllumeStylingSessions.objects.get(id =3)
        product_instance = Product.objects.get(id=1)

        # Have to create an object in order to delete it
        rack_instance = Rack.objects.create(product=product_instance, allume_styling_session=session_instance)

        url = reverse("shopping_tool_api:rack_item", kwargs={'pk':rack_instance.id})
        response = self.client.get(url)

        self.assertEqual(200, response.status_code)

    def test_add_look_item(self):
        """
        Test to verify adding a product to a look
        """
        url = reverse("shopping_tool_api:look_item", kwargs={'pk':0})

        data = {"layout_position": 4,"look": 1,"product": 1}
        response = self.client.put(url, data)

        look_products_count = Look.objects.get(id=1).product_set.count()

        self.assertEqual(201, response.status_code)
        self.assertEqual(LookProduct.objects.count(), 1)
        self.assertEqual(look_products_count, 1)


    def test_update_look_item(self):
        """
        Test to verify updating a product to a look
        """

         # Have to create an object in order to update it
        product_instance = Product.objects.get(id=1)
        look_instance = Look.objects.get(id=1)
        look_product_instance = LookProduct.objects.create(look = look_instance, product = product_instance, layout_position = 1)


        url = reverse("shopping_tool_api:look_item", kwargs={'pk':look_product_instance.id})

        data = {"layout_position": 1,"look": 1,"product": 1, "id": look_product_instance.id}
        response = self.client.put(url, data)

        updated_look_product_instance = LookProduct.objects.get(id=look_product_instance.id)

        self.assertEqual(201, response.status_code)
        self.assertEqual(updated_look_product_instance.layout_position, 1)

    def test_get_look_item(self):
        """
        Test to verify getting a look product
        """
        product_instance = Product.objects.get(id=1)
        look_instance = Look.objects.get(id=1)
        look_product_instance = LookProduct.objects.create(look = look_instance, product = product_instance, layout_position = 1)

        url = reverse("shopping_tool_api:look_item", kwargs={'pk':look_product_instance.id})

        response = self.client.get(url)
        response_look_product_id = json.loads(response.content)['product']['id']

        look_product_id = LookProduct.objects.get(id=look_product_instance.id).product.id

        self.assertEqual(200, response.status_code)
        self.assertEqual(look_product_id, response_look_product_id)

    def test_delete_look_item(self):
        """
        Test to verify deleting a product from a look
        """

        # Have to create an object in order to delete it
        product_instance = Product.objects.get(id=1)
        look_instance = Look.objects.get(id=1)
        look_product_instance = LookProduct.objects.create(look = look_instance, product = product_instance, layout_position = 1)

        url = reverse("shopping_tool_api:look_item", kwargs={'pk':look_product_instance.id})
        response = self.client.delete(url)

        self.assertEqual(201, response.status_code)


    def test_get_look_list(self):
        """
        Test to verify getting looks list
        """

        url = reverse("shopping_tool_api:look_list")
        

        #Test Getting UnFiltered List
        response_all = self.client.post(url)
        response_data_all = json.loads(response_all.content)
        self.assertEqual(len(response_data_all['looks']), 3)
        self.assertEqual(200, response_all.status_code)

        #Test Getting Client Filtered List
        client_filter_data = {"client": 8}
        response_client = self.client.post(url, client_filter_data)
        response_data_client = json.loads(response_client.content)
        self.assertEqual(len(response_data_client['looks']), 2)
        self.assertEqual(200, response_client.status_code)

        #Test Getting Stylist Filtered List
        stylist_filter_data = {"stylist": 117}
        response_stylist = self.client.post(url, stylist_filter_data)
        response_data_stylist = json.loads(response_stylist.content)
        self.assertEqual(len(response_data_stylist['looks']), 1)
        self.assertEqual(200, response_stylist.status_code)

        #Test Getting allume_styling_session Filtered List
        styling_session_filter_data = {"allume_styling_session": 3}
        response_styling_session = self.client.post(url, styling_session_filter_data)
        response_data_styling_session = json.loads(response_styling_session.content)
        self.assertEqual(len(response_data_styling_session['looks']), 2)
        self.assertEqual(200, response_styling_session.status_code)



    def test_get_look_list_paging(self):
        """
        Test to verify getting looks list with Paging
        """

        url = reverse("shopping_tool_api:look_list")

        #Test Paging
        paging_filter_data = {"per_page": 1}
        response_paging = self.client.post(url, paging_filter_data)
        response_data_paging = json.loads(response_paging.content)
        self.assertEqual(len(response_data_paging['looks']), 1)
        self.assertEqual(200, response_paging.status_code)



    def test_get_look_list_favorites(self):
        """
        Test to verify getting looks list filtered by favorites
        """

        NUM_USER_LOOK_FAVORITES = 4
        self.assertEqual(NUM_USER_LOOK_FAVORITES, UserLookFavorite.objects.count())

        url = reverse("shopping_tool_api:look_list")

        look_instance1 = Look.objects.get(id=1)
        look_instance2 = Look.objects.get(id=2)

        client = WpUsers.objects.filter(user_email= "client@allume.co").get()

        ulf1 = UserLookFavorite.objects.get(id=1)
        ulf2 = UserLookFavorite.objects.get(id=2)

        favs_filter_data = {"favorites_only": "True"}
        response_favs = self.client.post(url, favs_filter_data)
        response_data_favs = json.loads(response_favs.content)
        self.assertEqual(len(response_data_favs['looks']), 0)

        ulf1.stylist = client
        ulf1.save()
        ulf2.stylist = client
        ulf2.save()

        #Test Paging
        favs_filter_data = {"favorites_only": "True"}
        response_favs = self.client.post(url, favs_filter_data)

        response_data_favs = json.loads(response_favs.content)

        self.assertEqual(len(response_data_favs['looks']), 2)
        self.assertEqual(200, response_favs.status_code)



    def test_get_layouts(self):
        """
        Test to verify getting a look
        """

        url = reverse("shopping_tool_api:layouts")

        response = self.client.get(url)
        response_data = json.loads(response.content)[0]

        self.assertEqual(LookLayout.objects.get(id = 1).name, response_data['name'])
        self.assertEqual(200, response.status_code)



    def test_get_user_product_favorite(self):
        """
        Test to verify getting a user favorite look
        """

        url = reverse("shopping_tool_api:user_product_favorite", kwargs={'pk':1})

        response = self.client.get(url)
        self.assertEqual(200, response.status_code)


    def test_add_user_product_favorite(self):
        """
        Test to verify getting a user favorite look
        """

        url = reverse("shopping_tool_api:user_product_favorite", kwargs={'pk':1})
        data = {"product": 1,"stylist": 1}

        response = self.client.get(url, data)
        self.assertEqual(200, response.status_code)

    def test_delete_user_product_favorite(self):
        """
        Test to verify getting a user favorite look
        """

        url = reverse("shopping_tool_api:user_product_favorite", kwargs={'pk':1})

        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_user_product_favorites(self):
        """
        Test to verify getting a list of user favorite looks
        """

        url = reverse("shopping_tool_api:user_product_favorites", kwargs={'pk':1})

        response = self.client.get(url)
        self.assertEqual(200, response.status_code)


### Look Favs

    def test_get_user_look_favorite(self):
        """
        Test to verify getting a user favorite look
        """

        url = reverse("shopping_tool_api:user_look_favorite", kwargs={'pk':1})

        response = self.client.get(url)
        self.assertEqual(200, response.status_code)


    def test_add_user_look_favorite(self):
        """
        Test to verify adding a user favorite look
        """

        url = reverse("shopping_tool_api:user_look_favorite", kwargs={'pk':1})
        data = {"look": 1,"stylist": 2}

        response = self.client.get(url, data)
        self.assertEqual(200, response.status_code)

    def test_delete_user_look_favorite(self):
        """
        Test to verify deleting a user favorite look
        """

        url = reverse("shopping_tool_api:user_look_favorite", kwargs={'pk':1})

        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_user_look_favorites(self):
        """
        Test to verify getting a list of user favorite looks
        """

        url = reverse("shopping_tool_api:user_look_favorites", kwargs={'pk':1})

        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

### Client 360

    def test_get_client_360(self):
        """
        Test to verify getting a user favorite look
        """

        url = reverse("shopping_tool_api:client_360", kwargs={'pk':1})

        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        
