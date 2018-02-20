# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from django.core.urlresolvers import reverse

from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from shopping_tool_api.serializers import LookMetricsSerializer, LookSerializer

from shopping_tool.models import *
from django.http.cookie import SimpleCookie
from catalogue_service.settings_local import AUTH_LOGIN_URL, AUTH_EMAIL_KEY

#http://www.django-rest-framework.org/api-guide/testing/

class LookMetricsTestCase(APITestCase):

    fixtures = ['LookMetricsTestCase']

    def setUp(self):
        client = WpUsers.objects.create(user_email= "client@allume.co", user_phone=2, user_login='test2', is_superuser=1, is_staff=1, is_active=1, system_generated="No")
        self.client.cookies = SimpleCookie({AUTH_EMAIL_KEY: 'client@allume.co'})

    def test_lookmetrics_serializer(self):
        """
        Tests that the serializer is set up correctly.
        """
        lm = LookMetrics.objects.get(pk=1)
        serializer = LookMetricsSerializer(lm)
        # ascertain serializer data
        self.assertIsNotNone(serializer)
        json = serializer.data
        self.assertEqual(u'64.00', json['total_look_price'])
        self.assertEqual(1, json['look'])
        self.assertEqual(u'32.00', json['average_item_price'])
        self.assertEqual(3, json['total_favorites'])
        self.assertEqual(u'0.00', json['store_rank'])
        self.assertEqual(u'0.00', json['total_item_sales'])

    # test the lookmetrics serializer in the look serializer?
    def test_look_serializer(self):
        """
        Test that look_metrics field of a Look is setup correctly.
        """
        l = Look.objects.get(pk=1)
        serializer = LookSerializer(l)
        self.assertIsNotNone(serializer)
        json = serializer.data
        lookmetrics = json['look_metrics'][0]
        self.assertEqual(1, lookmetrics['look'])
        self.assertEqual(u'32.00', lookmetrics['average_item_price'])
        self.assertEqual(u'64.00', lookmetrics['total_look_price'])
        self.assertEqual(3, lookmetrics['total_favorites'])
        self.assertEqual(u'0.00', lookmetrics['total_item_sales'])
        self.assertEqual(u'0.00', lookmetrics['store_rank'])

    def test_get_look_list_total_look_price(self):
        """
        Tests the ability to get a look list and filter on total look price.
        """
        url = reverse("shopping_tool_api:look_list")

        # test on strictly less than
        total_look_price_filter_data = {'total_look_price_minimum': 100.00, 'total_look_price_maximum': 500.00}
        response = self.client.post(url, total_look_price_filter_data)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        # check length of looks returned
        self.assertEqual(6, len(data['looks']))
        # as well as the thresholds set in the filter?

        # test on less than or equal to
        total_look_price_filter_data = {'total_look_price_minimum': 700.00, 'total_look_price_maximum': 500.00}
        response = self.client.post(url, total_look_price_filter_data)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        # check length of looks returned
        self.assertEqual(0, len(data['looks']))
        # as well as the thresholds set in the filter

        # test on equal to exists
        total_look_price_filter_data = {'total_look_price_minimum': 1000.00, 'total_look_price_maximum': 2500.00}
        response = self.client.post(url, total_look_price_filter_data)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        # check length of looks returned
        self.assertEqual(2, len(data['looks']))
        # as well as the thresholds set in the filter

        # test on greater than or equal to
        total_look_price_filter_data = {'total_look_price_minimum': 400.00, 'total_look_price_maximum': 1000.00}
        response = self.client.post(url, total_look_price_filter_data)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        # check length of looks returned
        self.assertEqual(4, len(data['looks']))
        # as well as the thresholds set in the filter

        # test on strictly greater than
        total_look_price_filter_data = {'total_look_price_minimum': 250.00, 'total_look_price_maximum': 750.00}
        response = self.client.post(url, total_look_price_filter_data)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        # check length of looks returned
        self.assertEqual(3, len(data['looks']))
        # as well as the thresholds set in the filter

    def test_get_look_list_average_item_price(self):
        """
        Tests the ability to get a look list and filter on average item price.
        """
        url = reverse("shopping_tool_api:look_list")

        # test on strictly less than
        average_item_price_filter_data = {'average_item_price_minimum': 40.00, 'average_item_price_maximum': 80.00}
        response = self.client.post(url, average_item_price_filter_data)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        # check length of looks returned
        self.assertEqual(1, len(data['looks']))
        # as well as the thresholds set in the filter

        # test on less than or equal to
        average_item_price_filter_data = {'average_item_price_minimum': 10.00, 'average_item_price_maximum': 280.00}
        response = self.client.post(url, average_item_price_filter_data)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        # check length of looks returned
        self.assertEqual(13, len(data['looks']))
        # as well as the thresholds set in the filter

        # test on equal to exists
        average_item_price_filter_data = {'average_item_price_minimum': 400.00, 'average_item_price_maximum': 0.00}
        response = self.client.post(url, average_item_price_filter_data)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        # check length of looks returned
        self.assertEqual(0, len(data['looks']))
        # as well as the thresholds set in the filter

        # test on equal to does not exist
        average_item_price_filter_data = {'average_item_price_minimum': 400.00, 'average_item_price_maximum': 4000.00}
        response = self.client.post(url, average_item_price_filter_data)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        # check length of looks returned
        self.assertEqual(3, len(data['looks']))
        # as well as the thresholds set in the filter

        # test on greater than or equal to
        average_item_price_filter_data = {'average_item_price_minimum': 1.00, 'average_item_price_maximum': 500.00}
        response = self.client.post(url, average_item_price_filter_data)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        # check length of looks returned
        self.assertEqual(17, len(data['looks']))
        # as well as the thresholds set in the filter

    def test_both_lookmetrics_filters(self):
        """
        Tests the ability to filter on both of the filters used via LookMetrics
        """
        url = reverse("shopping_tool_api:look_list")

        filter_data = {'total_look_price_minimum': 1000.00, 'total_look_price_maximum': 2500.00,
                        'average_item_price_minimum': 900.00, 'average_item_price_maximum': 2000.00}
        response = self.client.post(url, filter_data)
        data = json.loads(response.content)
        # check lengths of looks returned
        self.assertEqual(2, len(data['looks']))

        filter_data = {'total_look_price_minimum': 400.00, 'total_look_price_maximum': 1000.00,
                        'average_item_price_minimum': 8.00, 'average_item_price_maximum': 400.00}

        response = self.client.post(url, filter_data)
        data = json.loads(response.content)
        # check length of looks returned
        self.assertEqual(4, len(data['looks']))


class ShoppingToolAPITestCase(APITestCase):
    
    fixtures = ['wpusers', 'allumestylingsessions', 'styling_session_notes', 'looklayout', 'look', 'product', 'user_product_favorite', 'allume_client_360_test', 'user_look_favorite', 'lookmetrics', 'look_products']

    shopper = ''
    client = ''

    def setUp(self):
        client = WpUsers.objects.create(user_email= "client@allume.co", user_phone=2, user_login='test2', is_superuser=1, is_staff=1, is_active=1, system_generated="No")
        self.client.cookies = SimpleCookie({AUTH_EMAIL_KEY: 'client@allume.co'})

    def test_create_look(self):
        """
        Test to verify creating a look
        """
        url = reverse("shopping_tool_api:look", kwargs={'pk':0})
        
        shopper = WpUsers.objects.create(user_email= "shopper@allume.co", user_phone=1, user_login='test1', is_superuser=1, is_staff=1, is_active=1, system_generated="No")
        data = {"name": "Api Test Look", "allume_styling_session": 1, "stylist": shopper.id}

        response = self.client.put(url, data)
        response_data = json.loads(response.content)


        self.assertEqual(201, response.status_code)
        self.assertEqual(Look.objects.count(), 4)
        self.assertEqual(Look.objects.get(id = response_data['id']).name, 'Api Test Look')
        # self.assertEqual(Look.objects.get(id = response_data['id']).look_layout.name, 'one_item')

    def test_create_note(self):
        """
        Test to verify creating a styling session note
        """
        url = reverse("shopping_tool_api:styling_session_note", kwargs={'pk':0})
        
        stylist = WpUsers.objects.create(user_email= "shopper@allume.co", user_phone=1, user_login='test1', is_superuser=1, is_staff=1, is_active=1, system_generated="No")
        data = {"notes": "Api Test Note", "styling_session": 1, "client": 5, "user_id": 6, "stylist": 6, "visible": 1}

        response = self.client.put(url, data)
        response_data = json.loads(response.content)

        self.assertEqual(201, response.status_code)
        self.assertEqual(AllumeUserStylistNotes.objects.count(), 3)
        self.assertEqual(AllumeUserStylistNotes.objects.get(id = response_data['id']).notes, 'Api Test Note')


    def test_get_note(self):
        """
        Test to verify getting a styling session note
        """
        url = reverse("shopping_tool_api:styling_session_note", kwargs={'pk':1})

        response = self.client.get(url)
        response_data = json.loads(response.content)

        self.assertEqual(AllumeUserStylistNotes.objects.get(id = 1).notes, response_data['notes'])
        self.assertEqual(200, response.status_code)

    def test_get_session_notes(self):
        """
        Test to verify getting a styling session note
        """
        url = reverse("shopping_tool_api:styling_session_notes", kwargs={'pk':1})

        response = self.client.get(url)
        response_data = json.loads(response.content)

        #self.assertEqual(AllumeUserStylistNotes.objects.get(id = 1).notes, response_data['notes'])
        self.assertEqual(200, response.status_code)


    def test_update_note(self):
        """
        Test to verify updating a a styling session note
        """

        note_instance = AllumeUserStylistNotes.objects.get(id=2)

        url = reverse("shopping_tool_api:styling_session_note", kwargs={'pk':note_instance.id})

        data = {"id": note_instance.id, "notes": "Api Test Update Note", "styling_session": note_instance.styling_session.id, "client": note_instance.client.id, "stylist": note_instance.stylist.id, "visible": note_instance.visible}

        #Verify the Original Look Name is in Place
        self.assertEqual(note_instance.notes, 'this is my second note')

        response = self.client.put(url, data)
        response_data = json.loads(response.content)

        #print response


        self.assertEqual(201, response.status_code)
        self.assertEqual(AllumeUserStylistNotes.objects.count(), 2)
        self.assertEqual(AllumeUserStylistNotes.objects.get(id = note_instance.id).notes, 'Api Test Update Note')


    def test_delete_note(self):
        """
        Test to verify deleting a styling session note
        """
        # successful delete
        url = reverse("shopping_tool_api:styling_session_note", kwargs={'pk': 1})

        self.assertEqual(2, AllumeUserStylistNotes.objects.count())

        response = self.client.delete(url)
        response_data = json.loads(response.content)

        self.assertTrue(response_data['Success'])
        self.assertEqual(201, response.status_code)
        self.assertEqual(1, AllumeUserStylistNotes.objects.count())

        # unsuccessful delete
        response = self.client.delete(url)
        response_data = json.loads(response.content)

        self.assertFalse(response_data['Success'])
        self.assertEqual(400, response.status_code)
        self.assertEqual(1, AllumeUserStylistNotes.objects.count())


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

        data = {"product": 1, "allume_styling_session": 3, "stylist": 5}
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
        stylist_filter_data = {"stylist": 9}
        response_stylist = self.client.post(url, stylist_filter_data)
        response_data_stylist = json.loads(response_stylist.content)
        self.assertEqual(len(response_data_stylist['looks']), 3)
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

    def test_update_look_position(self):
        """
        Test to verify updating the position of a look
        """
        LOOK_POSITION_DEFAULT = 100
        url = reverse("shopping_tool_api:update_look_position", kwargs={'pk':1})

        self.assertEqual(LOOK_POSITION_DEFAULT, Look.objects.get(pk=1).position)

        data = {"look_id": 1, "position": 4}

        response = self.client.put(url, data)
        response_data = json.loads(response.content)

        self.assertEqual(4, Look.objects.get(pk=1).position)

    def test_update_look_collage_image_data(self):
        """
        Test to verify updating the collage_image_data field of a look
        """
        url = reverse("shopping_tool_api:update_look_collage_image_data", kwargs={'pk':1})

        self.assertEqual(None, Look.objects.get(pk=1).collage)

        data = {"collage_image_data": "new info"}
        response = self.client.put(url, data)
        response_data = json.loads(response.content)

        self.assertEqual("new info", Look.objects.get(pk=1).collage)

    def test_update_cropped_image_code(self):
        """
        Test to verify updating the cropped_image_code field of a LookProduct
        """
        url = reverse("shopping_tool_api:update_cropped_image_code", kwargs={'pk': 4})

        lp = LookProduct.objects.get(pk=4)

        self.assertEqual(None, lp.cropped_image_code)

        data = {"cropped_image_code": "payload"}
        response = self.client.put(url, data)

        lp = LookProduct.objects.get(pk=4)

        self.assertEqual("payload", lp.cropped_image_code)

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
        
