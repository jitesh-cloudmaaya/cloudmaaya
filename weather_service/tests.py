# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.test import TestCase
from weather_service.models import Weather

class SingleWeatherRetrievalTests(TestCase):
    @classmethod
    def setUpTestData(cls):
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


    # other edge cases




        # is this a mysql (used in dev) vs sqlite (used in test) string comparison thing
    # def test_retrieval_using_uncapitalized_city_state(self):
    #     """
    #     Test city and state string formatting behavior of Weather object.
    #     """
    #     pass
    #     # BREAKS CIRLCECI because of db difference
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

# test update weather data
class UpdateOnStaleDataTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.CURRENT_YEAR = datetime.datetime.now().year
        cls.LAST_UPDATED_YEAR_1 = 2012
        cls.LAST_UPDATED_YEAR_2 = 2010
        cls.LAST_UPDATED_YEAR_3 = 2008
        cls.LAST_UPDATED_YEAR_4 = 2007
        cls.LAST_UPDATED_YEAR_5 = 2015
        cls.FRESH_YEAR = datetime.datetime.now().year - 1

        # cls.LAST_UPDATED_MONTH = 

    fixtures = ['UpdateOnStaleDataTests']

    def test_update_stale_data_single(self):
        w = Weather.objects.get(city='San Jose', state='CA')
        last_modified_year = w.last_modified.year
        self.assertEqual(self.LAST_UPDATED_YEAR_1, last_modified_year)
        w = Weather.objects.retrieve_weather_object(city='San Jose', state='CA')
        self.assertEqual(self.CURRENT_YEAR, w.last_modified.year)

        w = Weather.objects.get(city='San Diego', state='CA')
        last_modified_year = w.last_modified.year
        self.assertEqual(self.LAST_UPDATED_YEAR_2, last_modified_year)
        w = Weather.objects.retrieve_weather_object(city='San Diego', state='CA')
        self.assertEqual(self.CURRENT_YEAR, w.last_modified.year)

        w = Weather.objects.get(city='San Francisco', state='CA')
        last_modified_year = w.last_modified.year
        self.assertEqual(self.LAST_UPDATED_YEAR_3, last_modified_year)
        w = Weather.objects.retrieve_weather_object(city='San Francisco', state='CA')
        self.assertEqual(self.CURRENT_YEAR, w.last_modified.year)

    # def test_update_stale_data_bulk(self):
    #     w0 = Weather.objects.get(city='San Francisco', state='CA')
    #     w1 = Weather.objects.get(city='Merced', state='CA')
    #     w2 = Weather.objects.get(city='Tracy', state='CA')

    #     last_modified_year0 = w0.last_modified.year
    #     last_modified_year1 = w1.last_modified.year
    #     last_modified_year2 = w2.last_modified.year

    #     self.assertEqual(self.LAST_UPDATED_YEAR_3, last_modified_year0)
    #     self.assertEqual(self.LAST_UPDATED_YEAR_4, last_modified_year1)
    #     self.assertEqual(self.LAST_UPDATED_YEAR_5, last_modified_year2)

    #     locations = [('San Francisco', 'CA'), ('Merced', 'CA'), ('Tracy', 'CA')]
    #     weathers = Weather.objects.retrieve_weather_objects(locations)
    #     for weather in weathers:
    #         self.assertEqual(self.CURRENT_YEAR, weather.last_modified.year)

    def test_no_update_fresh_data_single(self):
        w = Weather.objects.get(city='Azusa', state='CA')
        weather = Weather.objects.retrieve_weather_object(city='Azusa', state='CA')
        self.assertEqual(w.last_modified, weather.last_modified)

    def test_no_update_fresh_data_bulk(self):
        w0 = Weather.objects.get(city='Azusa', state='CA')
        w1 = Weather.objects.get(city='Claremont', state='CA')
        w2 = Weather.objects.get(city='Fresno', state='CA')

        last_modifieds = [w0.last_modified, w1.last_modified, w2.last_modified]
        locations = [('Azusa', 'CA'), ('Claremont', 'CA'), ('Fresno', 'CA')]
        weathers = Weather.objects.retrieve_weather_objects(locations)
        for i in range(0, len(weathers)):
            self.assertEqual(last_modifieds[i], weathers[i].last_modified)


class WeatherIconPropertyTests(TestCase):
    """
    Testing strategy:

    Create 4 to 5 Weather objects of differing values and test that they give the expected icons.
    """
    @classmethod
    def setUpTestData(cls):
        pass
        

    fixtures = ["WeatherIconPropertyTests"]

    # assertEqual(expected, actual)
    def test_sunny_icon(self):
        w = Weather.objects.get(pk=1)
        self.assertEqual('wi-day-sunny', w.icon)
        # test a few different ways?
        

    def test_windy_icon(self):
        w = Weather.objects.get(pk=2)
        self.assertEqual('wi-day-cloudy-windy', w.icon)

    def test_gusty_icon(self):
        w = Weather.objects.get(pk=3)
        self.assertEqual('wi-day-cloudy-gusts', w.icon)

    def test_rainy_icon(self):
        w = Weather.objects.get(pk=4)
        self.assertEqual('wi-day-rain', w.icon)

    def test_snowy_icon(self):
        w = Weather.objects.get(pk=5)
        self.assertEqual('wi-day-snow', w.icon)


    # def test zero behavior
    # test on no-zip code and no-data

    # additional testing thoughts, may have to test by season if methods get split up
    # create redundant tests for each season icon method to ensure behavior???

    def test_winter_sunny_icon(self):
        pass





    #     if self.summer_sun >= 50:
    #         icon_id = 'wi-day-sunny'
    #     if self.summer_wind >= 8:
    #         icon_id = 'wi-day-cloudy-windy'
    #     if self.summer_wind > 15:
    #         icon_id = 'wi-day-cloudy-gusts'
    #     if self.summer_precipitation > 3:
    #         icon_id = 'wi-day-rain'
    #     if self.summer_snowfall > 2:
    #         icon_id = 'wi-day-snow'
        
        # return icon_id




            # if self.summer_sun >= 50:
            #     icon_id = 'wi-day-sunny'
            # if self.summer_wind >= 8:
            #     icon_id = 'wi-day-cloudy-windy'
            # if self.summer_wind > 15:
            #     icon_id = 'wi-day-cloudy-gusts'
            # if self.summer_precipitation > 3:
            #     icon_id = 'wi-day-rain'
            # if self.summer_snowfall > 2:
            #     icon_id = 'wi-day-snow'








