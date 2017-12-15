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
        Behavior now asserts that objects are created as long as a city and state are provided,
        but both locations with no zip codes or no data are initialized to have zeros in weather data.
        """
        # locations with no zip codes or no data for zip codes initialize with zeros
        self.assertEqual(self.EXPECTED_WEATHER_COUNT, Weather.objects.count())
        self.assertEqual(0.0, Weather.objects.retrieve_weather_object(city='Atlantis', state='OC').spring_wind) # fake city and state
        self.assertEqual(self.EXPECTED_WEATHER_COUNT+1, Weather.objects.count())
        self.assertEqual(0.0, Weather.objects.retrieve_weather_object(city='San Jose', state='MD').summer_wind) # mismatched city and state
        self.assertEqual(self.EXPECTED_WEATHER_COUNT+2, Weather.objects.count())
        self.assertIsNone(Weather.objects.retrieve_weather_object(city='Emerald City', state='OZ').winter_temperature_average) # fake city
        self.assertEqual(self.EXPECTED_WEATHER_COUNT+3, Weather.objects.count())
        self.assertEqual(0.0, Weather.objects.retrieve_weather_object(city='Merced', state='RA').autumn_snowfall) # fake state
        self.assertEqual(self.EXPECTED_WEATHER_COUNT+4, Weather.objects.count())

    def test_retrieve_weather_empty(self):
        """
        Test the behavior of retrieve_weather_object method when provided with empty strings
        for one or more arguments. Behavior now asserts that objects are created as long as
        a city and state are provided, but both locations with no zip codes or no data are
        initialized to have zeros in weather data.
        """
        # locations with no zip codes or no data for zip codes initialize with zeros
        self.assertEqual(self.EXPECTED_WEATHER_COUNT, Weather.objects.count())
        self.assertIsNone(Weather.objects.retrieve_weather_object(city='', state='').spring_temperature_average)
        self.assertEqual(self.EXPECTED_WEATHER_COUNT+1, Weather.objects.count())
        self.assertEqual(0.0, Weather.objects.retrieve_weather_object(city='San Jose', state='').summer_precipitation)
        self.assertEqual(self.EXPECTED_WEATHER_COUNT+2, Weather.objects.count())
        self.assertEqual(0.0, Weather.objects.retrieve_weather_object(city='', state='CA').autumn_sun)
        self.assertEqual(self.EXPECTED_WEATHER_COUNT+3, Weather.objects.count())


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


class UpdateOnStaleDataTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.CURRENT_YEAR = datetime.datetime.now().year

    fixtures = ['UpdateOnStaleDataTests']

    def test_update_stale_data_single(self):
        """
        Test the update of a single Weather object that has stale data.
        """
        w = Weather.objects.get(pk=1)
        self.assertNotEqual(self.CURRENT_YEAR, w.last_modified.year)
        w = Weather.objects.retrieve_weather_object(city='San Jose', state='CA')
        self.assertEqual(self.CURRENT_YEAR, w.last_modified.year)

        w = Weather.objects.get(pk=2)
        self.assertNotEqual(self.CURRENT_YEAR, w.last_modified.year)
        w = Weather.objects.retrieve_weather_object(city='San Diego', state='CA')
        self.assertEqual(self.CURRENT_YEAR, w.last_modified.year)

        w = Weather.objects.get(pk=3)
        self.assertNotEqual(self.CURRENT_YEAR, w.last_modified.year)
        w = Weather.objects.retrieve_weather_object(city='San Francisco', state='CA')
        self.assertEqual(self.CURRENT_YEAR, w.last_modified.year)

    def test_update_stale_data_bulk(self):
        """
        Test the update of a multiple Weather objects at one time that have stale data.
        """
        w0 = Weather.objects.get(pk=3)
        w1 = Weather.objects.get(pk=4)
        w2 = Weather.objects.get(pk=5)

        self.assertNotEqual(self.CURRENT_YEAR, w0.last_modified.year)
        self.assertNotEqual(self.CURRENT_YEAR, w1.last_modified.year)
        self.assertNotEqual(self.CURRENT_YEAR, w2.last_modified.year)

        locations = [('San Francisco', 'CA'), ('Merced', 'CA'), ('Tracy', 'CA')]
        weathers = Weather.objects.retrieve_weather_objects(locations)
        for weather in weathers:
            self.assertEqual(self.CURRENT_YEAR, weather.last_modified.year)

    def test_no_update_fresh_data_single(self):
        """
        Test that a Weather object that has fresh data is not updated.
        """
        w = Weather.objects.get(pk=6)
        weather = Weather.objects.retrieve_weather_object(city='Azusa', state='CA')
        self.assertEqual(w.last_modified, weather.last_modified)

    def test_no_update_fresh_data_bulk(self):
        """
        Test that retrieving multiple Weather objects with fresh data are not updated.
        """
        w0 = Weather.objects.get(pk=6)
        w1 = Weather.objects.get(pk=7)
        w2 = Weather.objects.get(pk=8)

        last_modifieds = [w0.last_modified, w1.last_modified, w2.last_modified]
        locations = [('Azusa', 'CA'), ('Claremont', 'CA'), ('Fresno', 'CA')]
        weathers = Weather.objects.retrieve_weather_objects(locations)
        for i in range(0, len(weathers)):
            self.assertEqual(last_modifieds[i], weathers[i].last_modified)

    def test_update_only_stale_bulk(self):
        """
        Test that, in a bulk update, only Weathers that have stale data are updated.
        """
        # current setup is w0 and w1 are stale, w2 and w3 are recent

        w0 = Weather.objects.get(pk=9)
        w1 = Weather.objects.get(pk=10)
        w2 = Weather.objects.get(pk=11)
        w3 = Weather.objects.get(pk=12)

        self.assertNotEqual(self.CURRENT_YEAR, w0.last_modified.year)
        self.assertNotEqual(self.CURRENT_YEAR, w1.last_modified.year)

        locations = [('Denver', 'CO'), ('Atlanta', 'GA'), ('Boston', 'MA'), ('Dallas', 'TX')]
        weathers = Weather.objects.retrieve_weather_objects(locations)

        self.assertEqual(self.CURRENT_YEAR, weathers[0].last_modified.year)
        self.assertEqual(self.CURRENT_YEAR, weathers[1].last_modified.year)

        self.assertEqual(w2.last_modified, weathers[2].last_modified)
        self.assertEqual(w3.last_modified, weathers[3].last_modified)


class WeatherIconPropertyTests(TestCase):
    """
    Testing strategy:

    Create 4 to 5 Weather objects of differing values and test that they give the expected icons.
    """
    @classmethod
    def setUpTestData(cls):
        pass
        
    fixtures = ["WeatherIconPropertyTests"]

    # single case tests
    def test_cloudy_icon(self):
        """
        Test cloudy icon conditions.
        """
        w = Weather.objects.get(pk=1)
        self.assertEqual('wi-day-cloudy', w.summer_icon)
        # self.assertEqual('wi-day-cloudy', w.winter_icon)

    def test_sunny_icon(self):
        """
        Test sunny icon conditions.
        """
        w = Weather.objects.get(pk=2)
        self.assertEqual('wi-day-sunny', w.summer_icon)

    def test_windy_icon(self):
        """
        Test windy icon conditions.
        """
        w = Weather.objects.get(pk=3)
        self.assertEqual('wi-day-light-wind', w.summer_icon)

    def test_cloudy_windy_icon(self):
        """
        Test cloudy and windy icon conditions.
        """
        w = Weather.objects.get(pk=4)
        self.assertEqual('wi-day-cloudy-windy', w.summer_icon)

    def test_gusty_icon(self):
        """
        Test gusty icon conditions.
        """
        w = Weather.objects.get(pk=5)
        self.assertEqual('wi-day-windy', w.summer_icon)

    def test_cloudy_gusty_icon(self):
        """
        Test cloudy and gusty icon conditions.
        """
        w = Weather.objects.get(pk=6)
        self.assertEqual('wi-day-cloudy-gusts', w.summer_icon)

    def test_rainy_icon(self):
        """
        Test rainy icon conditions.
        """
        w = Weather.objects.get(pk=7)
        self.assertEqual('wi-day-rain', w.summer_icon)

    def test_rainy_windy_icon(self):
        """
        Test rainy and windy icon conditions.
        """
        w = Weather.objects.get(pk=8)
        self.assertEqual('wi-day-rain-wind', w.summer_icon)

    def test_snowy_icon(self):
        """
        Test snowy icon conditions.
        """
        w = Weather.objects.get(pk=9)
        self.assertEqual('wi-day-snow', w.summer_icon)

    def test_snowy_windy_icon(self):
        """
        Test snowy and windy icon conditions.
        """
        w = Weather.objects.get(pk=10)
        self.assertEqual('wi-day-snow-wind', w.summer_icon)

    def test_default_weather(self):
        """
        Test default Weather object returns default icon.
        """
        w = Weather.objects.get(pk=11)
        self.assertEqual('wi-day-cloudy', w.summer_icon)

    def test_zeroes_icon(self):
        """
        Test that icon selection is default when all data is set to zero.
        """
        w = Weather.objects.get(pk=17)
        self.assertEqual('wi-day-cloudy', w.summer_icon)

    # test case hierarchy (sun/cloud < wind < rain < snow)
    def test_icon_hierarchy(self):
        """
        Test that ceratin icon case conditions overrule others (e.g. 
        all conditions lose to snow).
        """
        w = Weather.objects.get(pk=12)
        self.assertEqual('wi-day-rain-wind', w.summer_icon)
        w = Weather.objects.get(pk=13)
        self.assertEqual('wi-day-snow-wind', w.summer_icon)
        w = Weather.objects.get(pk=14)
        self.assertEqual('wi-day-snow-wind', w.summer_icon)
        w = Weather.objects.get(pk=15)
        self.assertEqual('wi-day-snow-wind', w.summer_icon)
        
    def test_different_icons(self):
        """
        Test that Weather objets with different attributes for 
        different seasons return appropriate icons.
        """
        w = Weather.objects.get(pk=16)
        self.assertEqual('wi-day-cloudy', w.spring_icon)
        self.assertEqual('wi-day-rain-wind', w.summer_icon)
        self.assertEqual('wi-day-cloudy-gusts', w.autumn_icon)
        self.assertEqual('wi-day-snow', w.winter_icon)




