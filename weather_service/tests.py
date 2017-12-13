# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.test import TestCase
from .models import Weather

# test update weather data
class UpdateOnStaleDataTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.CURRENT_YEAR = datetime.datetime.now().year
        cls.LAST_UPDATED_YEAR = 2012


    fixtures = ['UpdateOnStaleDataTests']

    def test(self):
        w = Weather.objects.get(city='San Jose', state='CA')
        last_modified_year = w.last_modified.year
        self.assertEqual(self.LAST_UPDATED_YEAR, last_modified_year)
        w = Weather.objects.retrieve_weather_object(city='San Jose', state='CA')
        self.assertEqual(self.CURRENT_YEAR, w.last_modified.year)


class SingleWeatherRetrievalTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Weather.objects.create(city='San Jose', state='CA')
        cls.EXPECTED_WEATHER_COUNT = 3

    fixtures = ['SingleWeatherRetrievalTests']


    def test_retrieve_existing_weather(self):
        """
        Test Weather retrieval on existing Weather object.
        """
        self.assertEqual(self.EXPECTED_WEATHER_COUNT, Weather.objects.count())
        self.assertEqual('San Jose', Weather.objects.retrieve_weather_object(city='San Jose', state='CA').city)
        self.assertEqual(self.EXPECTED_WEATHER_COUNT, Weather.objects.count())

    def test_retrieve_non_existing_weather(self):
        """
        Test Weather retrieval on not yet existing Weather object.
        """
        self.assertEqual(self.EXPECTED_WEATHER_COUNT, Weather.objects.count())
        self.assertEqual('San Diego', Weather.objects.retrieve_weather_object(city='San Diego', state='CA').city)
        self.assertEqual(self.EXPECTED_WEATHER_COUNT+1, Weather.objects.count())

    def test_retrieve_weather_from_non_existing_location(self):
        """
        Test Weather retrieval method behavior on being queried for non-existent location.
        """
        self.assertEqual(self.EXPECTED_WEATHER_COUNT, Weather.objects.count())
        # non-existent locations do not write to DB
        self.assertIsNone(Weather.objects.retrieve_weather_object(city='Atlantis', state='OC')) # fake city and state
        self.assertEqual(self.EXPECTED_WEATHER_COUNT, Weather.objects.count())
        self.assertIsNone(Weather.objects.retrieve_weather_object(city='San Jose', state='MD')) # mismatched city and state
        self.assertEqual(self.EXPECTED_WEATHER_COUNT, Weather.objects.count())
        self.assertIsNone(Weather.objects.retrieve_weather_object(city='Emerald City', state='OZ')) # fake city
        self.assertEqual(self.EXPECTED_WEATHER_COUNT, Weather.objects.count())
        self.assertIsNone(Weather.objects.retrieve_weather_object(city='Merced', state='RA')) # fake state
        self.assertEqual(self.EXPECTED_WEATHER_COUNT, Weather.objects.count())

    def test_retrieve_weather_empty(self):
        """
        Test the behavior of retrieve_weather_object method when provided with empty strings
        for one or more arguments.
        """
        self.assertEqual(self.EXPECTED_WEATHER_COUNT, Weather.objects.count())
        self.assertIsNone(Weather.objects.retrieve_weather_object(city='', state=''))
        self.assertEqual(self.EXPECTED_WEATHER_COUNT, Weather.objects.count())
        self.assertIsNone(Weather.objects.retrieve_weather_object(city='San Jose', state=''))
        self.assertEqual(self.EXPECTED_WEATHER_COUNT, Weather.objects.count())
        self.assertIsNone(Weather.objects.retrieve_weather_object(city='', state='CA'))
        self.assertEqual(self.EXPECTED_WEATHER_COUNT, Weather.objects.count())


        # is this a mysql (used in dev) vs sqlite (used in test) string comparison thing
    # def test_retrieval_using_uncapitalized_city_state(self):
    #     """
    #     Test city and state string formatting behavior of Weather object.
    #     """
    #     pass
    #     # BREAKS CIRLCECI
    #     print(Weather.objects.all())
    #     print(Weather.objects.count())
    #     self.assertEqual('San Jose', Weather.objects.retrieve_weather_object(city='san jose', state='CA').city)
    #     print(Weather.objects.all())
    #     print(Weather.objects.count())
    #     self.assertEqual('CA', Weather.objects.retrieve_weather_object(city='San Francisco', state='ca').state)
    #     print(Weather.objects.all())
    #     print(Weather.objects.count())
    #     w = Weather.objects.retrieve_weather_object(city='mountain view', state='ca')
    #     print(Weather.objects.all())
    #     print(Weather.objects.count())
    #     self.assertEqual(self.EXPECTED_WEATHER_COUNT, Weather.objects.count())
    #     print(Weather.objects.all())
    #     print(Weather.objects.count())
    #     self.assertEqual('Mountain View', w.city)
    #     print(Weather.objects.all())
    #     print(Weather.objects.count())
    #     self.assertEqual('CA', w.state)
    #     print(Weather.objects.all())
    #     print(Weather.objects.count())


    def test_retrieval_time_limit(self):
        """
        Test that a Weather object gets updated if its data is not recent enough.
        """
        pass

    # def tearDown(self):
    #     print('happens after every test')

class BulkWeatherRetrievalTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        pass

    fixtures = ['BulkWeatherRetrievalTests']

    def test_bulk_retrieve_existing_weather_all_exist(self):
        """
        Test small bulk retrieval of pre-existing Weather objects.
        """
        self.assertEqual(3, Weather.objects.count())
        weathers = Weather.objects.retrieve_weather_objects([('Boston', 'MA'), ('Richmond', 'VA'), ('Sacramento', 'CA')])
        self.assertEqual('Boston', weathers[0].city)
        self.assertEqual('Richmond', weathers[1].city)
        self.assertEqual('Sacramento', weathers[2].city)
        self.assertEqual('MA', weathers[0].state)
        self.assertEqual('VA', weathers[1].state)
        self.assertEqual('CA', weathers[2].state)
        self.assertEqual(3, Weather.objects.count())

    def test_bulk_retrieve_existing_weather_some_exist(self):
        """
        Test small bulk retrieval of Weather objects where some do not yet exist.
        """
        self.assertEqual(3, Weather.objects.count())
        weathers = Weather.objects.retrieve_weather_objects([('Atlanta', 'GA'), ('Boston', 'MA'), ('Phoenix', 'AZ')])
        self.assertEqual('Atlanta', weathers[0].city)
        self.assertEqual('Boston', weathers[1].city)
        self.assertEqual('Phoenix', weathers[2].city)
        self.assertEqual('GA', weathers[0].state)
        self.assertEqual('MA', weathers[1].state)
        self.assertEqual('AZ', weathers[2].state)
        self.assertEqual(5, Weather.objects.count())

    def test_bulk_retrieve_existing_weather_none_exist(self):
        """
        Test small bulk retrieval of Weather objects where none of the objects yet exist.
        """
        self.assertEqual(3, Weather.objects.count())
        weathers = Weather.objects.retrieve_weather_objects([('Philadelphia', 'PA'), ('New York', 'NY'), ('Houston', 'TX')])
        self.assertEqual('Philadelphia', weathers[0].city)
        self.assertEqual('New York', weathers[1].city)
        self.assertEqual('Houston', weathers[2].city)
        self.assertEqual('PA', weathers[0].state)
        self.assertEqual('NY', weathers[1].state)
        self.assertEqual('TX', weathers[2].state)
        self.assertEqual(6, Weather.objects.count())



