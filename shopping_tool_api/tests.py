# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from django.core.urlresolvers import reverse

from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from shopping_tool_api.serializers import LookMetricsSerializer

from shopping_tool.models import *
from django.http.cookie import SimpleCookie
from catalogue_service.settings_local import AUTH_LOGIN_URL, AUTH_EMAIL_KEY

#http://www.django-rest-framework.org/api-guide/testing/

class LookMetricsTestCase(APITestCase):

    # added look_metrics to end of fixtures
    # fixtures = ['wpusers', 'allumestylingsessions', 'looklayout', 'look', 'product', 'user_product_favorite', 'allume_client_360_test', 'user_look_favorite', 'lookmetrics']
    fixtures = ['lookmetrics']

    def setUp(self):
        client = WpUsers.objects.create(user_email= "client@allume.co", user_phone=2, user_login='test2', is_superuser=1, is_staff=1, is_active=1, system_generated="No")
        self.client.cookies = SimpleCookie({AUTH_EMAIL_KEY: 'client@allume.co'})
        # pass

    def test(self):
        lm = LookMetrics.objects.get(pk=1)
        print lm.look

    def test_django_filters(self):
        """
        Try to figure out django filter chaining to access a LookMetric from a Look
        """
        look = Look.objects.get(pk=1)
        print look.token
        Look.objects.filter()

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


    # space for debugging tests

    def test_multipart(self):
        """
        Explore multipart error
        """
        print('========================== BEGIN =========================')
        url = reverse("shopping_tool_api:look_list")

        # total_look_price_filter_data = {'tlp_filter': {'total_look_price': 400.00, 'comparison': 'lt'}}

        total_look_price_filter_data = {'total_look_price': 400.00, 'comparison': 'lt'}
        response = self.client.post(url, total_look_price_filter_data)
        print response
        print response.content
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        print data
        self.assertEqual(14, len(data['looks']))
        print('========================== END =========================')

    def test_w_simple_data(self):
        """
        use only one variable for data1=
        """
        url = reverse("shopping_tool_api:look_list")

        filter_data = {'total_look_price': 400.00}
        response = self.client.post(url, filter_data)
        self.assertEqual(200, response.status_code)
        print 'success'

    def test_w_simple_data2(self):
        """
        use one variable that's already been done in view look_list
        """
        url = reverse("shopping_tool_api:look_list")

        filter_data = {'client': 1}
        response = self.client.post(url, filter_data)
        self.assertEqual(200, response.status_code)
        print 'success'

    # end space for debugging tests

    # separate tests into smaller units?
    def test_get_look_list_total_look_price(self):
        """
        Tests the ability to get a look list and filter on total look price.
        """
        url = reverse("shopping_tool_api:look_list")

        # test on strictly less than
        total_look_price_filter_data = {'tlp_filter': {'total_look_price': 400.00, 'comparison': 'lt'}}
        response = self.client.post(url, total_look_price_filter_data)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        # check length of looks returned
        print data
        self.assertEqual(14, len(data['looks']))
        # as well as the thresholds set in the filter?

        # test on less than or equal to
        total_look_price_filter_data = {'tlp_filter': {'total_look_price': 36.20, 'comparison': 'lte'}}
        response = self.client.post(url, total_look_price_filter_data)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        # check length of looks returned
        self.assertEqual(2, len(data['looks']))
        # as well as the thresholds set in the filter

        # test on equal to exists
        total_look_price_filter_data = {'tlp_filter': {'total_look_price': 1.00, 'comparison': 'e'}}
        response = self.client.post(url, total_look_price_filter_data)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        # check length of looks returned
        self.assertEqual(1, len(data['looks']))
        # as well as the thresholds set in the filter

        # test on equal to does not exist
        total_look_price_filter = {'tlp_filter': {'total_look_price': 13.13, 'comparison': 'e'}}
        response = self.client.post(url, total_look_price_filter_data)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        # check lengths of looks returned
        self.assertEqual(0, len(data['looks']))
        # as well as the thresholds set in the filter

        # test on greater than or equal to
        total_look_price_filter_data = {'tlp_filter': {'total_look_price': 1840.00, 'comparison': 'gte'}}
        response = self.client.post(url, total_look_price_filter_data)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        # check length of looks returned
        self.assertEqual(2, len(data['looks']))
        # as well as the thresholds set in the filter

        # test on strictly greater than
        total_look_price_filter_data = {'tlp_filter': {'total_look_price': 3000.00, 'comparison': 'gt'}}
        response = self.client.post(url, total_look_price_filter_data)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        # check length of looks returned
        self.assertEqual(1, len(data['looks']))
        # as well as the thresholds set in the filter

    def test_get_look_list_average_item_price(self):
        """
        Tests the ability to get a look list and filter on average item price.
        """
        url = reverse("shopping_tool_api:look_list")

        # all total_look_prices are placeholders until more interesting data is defined in fixture

        # test on strictly less than
        average_item_price_filter_data = {'aip_filter': {'average_item_price': 40.00, 'comparison': 'lt'}}
        response = self.client.post(url, average_item_price_filter_data)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        # check length of looks returned
        self.assertEqual(10, len(data['looks']))
        # as well as the thresholds set in the filter

        # test on less than or equal to
        average_item_price_filter_data = {'aip_filter': {'average_item_price': 40.00, 'comparison': 'lt'}}
        response = self.client.post(url, average_item_price_filter_data)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        # check length of looks returned
        self.assertEqual(11, len(data['looks']))
        # as well as the thresholds set in the filter

        # test on equal to exists
        average_item_price_filter_data = {'aip_filter': {'average_item_price': 18.10, 'comparison': 'e'}}
        response = self.client.post(url, average_item_price_filter_data)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        # check length of looks returned
        self.assertEqual(1, len(data['looks']))
        # as well as the thresholds set in the filter

        # test on equal to does not exist
        average_item_price_filter_data = {'aip_filter': {'average_item_price': 10.18, 'comparison': 'e'}}
        response = self.client.post(url, average_item_price_filter_data)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        # check length of looks returned
        self.assertEqual(0, len(data['looks']))
        # as well as the thresholds set in the filter

        # test on greater than or equal to
        average_item_price_filter_data = {'aip_filter': {'average_item_price': 300.03, 'comparison': 'gte'}}
        response = self.client.post(url, average_item_price_filter_data)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        # check length of looks returned
        self.assertEqual(5, len(data['looks']))
        # as well as the thresholds set in the filter

        # test on strictly greater than
        average_item_price_filter_data = {'aip_filter': {'average_item_price': 100.00, 'comparison': 'gt'}}
        response = self.client.post(url, average_item_price_filter_data)
        self.assertEqual(200, response.status_code)
        data = json.loads(response.content)
        # check length of looks returned
        self.assertEqual(9, len(data['looks']))
        # as well as the thresholds set in the filter

    # def test_get_look_list(self):
    #     """
    #     Test to verify getting looks list
    #     """

    #     url = reverse("shopping_tool_api:look_list")
        

    #     #Test Getting UnFiltered List
    #     response_all = self.client.post(url)
    #     response_data_all = json.loads(response_all.content)
    #     self.assertEqual(len(response_data_all['looks']), 3)
    #     self.assertEqual(200, response_all.status_code)

    #     #Test Getting Client Filtered List
    #     client_filter_data = {"client": 8}
    #     response_client = self.client.post(url, client_filter_data)
    #     response_data_client = json.loads(response_client.content)
    #     self.assertEqual(len(response_data_client['looks']), 2)
    #     self.assertEqual(200, response_client.status_code)

    #     #Test Getting Stylist Filtered List
    #     stylist_filter_data = {"stylist": 9}
    #     response_stylist = self.client.post(url, stylist_filter_data)
    #     response_data_stylist = json.loads(response_stylist.content)
    #     self.assertEqual(len(response_data_stylist['looks']), 3)
    #     self.assertEqual(200, response_stylist.status_code)

    #     #Test Getting allume_styling_session Filtered List
    #     styling_session_filter_data = {"allume_styling_session": 3}
    #     response_styling_session = self.client.post(url, styling_session_filter_data)
    #     response_data_styling_session = json.loads(response_styling_session.content)
    #     self.assertEqual(len(response_data_styling_session['looks']), 2)
    #     self.assertEqual(200, response_styling_session.status_code)

class ShoppingToolAPITestCase(APITestCase):
    
    fixtures = ['wpusers', 'allumestylingsessions', 'looklayout', 'look', 'product', 'user_product_favorite', 'allume_client_360_test', 'user_look_favorite']
    shopper = ''
    client = ''

    def setUp(self):        
        client = WpUsers.objects.create(user_email= "client@allume.co", user_phone=2, user_login='test2', is_superuser=1, is_staff=1, is_active=1, system_generated="No")
        self.client.cookies = SimpleCookie({AUTH_EMAIL_KEY: 'client@allume.co'})


    #     #Test Getting Client Filtered List
    #     client_filter_data = {"client": 8}
    #     response_client = self.client.post(url, client_filter_data)
    #     response_data_client = json.loads(response_client.content)
    #     self.assertEqual(len(response_data_client['looks']), 2)
    #     self.assertEqual(200, response_client.status_code)


    # def test_other(self):
    #     """
    #     use already working to see where going wrong
    #     """
    #     url = reverse("shopping_tool_api:look_list")

    #     client_filter_data = {"client": 8}
    #     response_client = self.client.post(url, client_filter_data)
    #     print('checking status code')
    #     self.assertEqual(200, response_client.status_code)
    #     print(response_client.status_code)
    #     response_data_client = json.loads(response_client.content)
    #     print('checking response data')
    #     self.assertEqual(2, len(response_data_client['looks']))
    #     print(response_data_client)

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
        print response_data_client
        self.assertEqual(len(response_data_client['looks']), 2)
        self.assertEqual(200, response_client.status_code)

        #Test Getting Stylist Filtered List
        stylist_filter_data = {"stylist": 9}
        response_stylist = self.client.post(url, stylist_filter_data)
        response_data_stylist = json.loads(response_stylist.content)
        print response_data_stylist
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

        url = reverse("shopping_tool_api:look_list")

        look_instance1 = Look.objects.get(id=1)
        look_instance2 = Look.objects.get(id=2)

        client = WpUsers.objects.filter(user_email= "client@allume.co").get()

        UserLookFavorite.objects.create(look=look_instance1, stylist = client)
        UserLookFavorite.objects.create(look=look_instance2, stylist = client)

        #Test Paging
        favs_filter_data = {"favorites_only": "True"}
        response_favs = self.client.post(url, favs_filter_data)
        response_data_favs = json.loads(response_favs.content)

        #self.assertEqual(len(response_data_favs['looks']), 2)
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
        
