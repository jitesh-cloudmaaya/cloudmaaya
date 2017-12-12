# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import time

from django.test import TestCase
from .models import Weather

class SingleWeatherRetrievalTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Weather.objects.create(city='San Jose', state='CA')

    # def testTest(self):
    #     self.assertEqual(True, True)

    def test_retrieve_existing_weather(self):
        print('running 1st test')
        self.assertEqual(1, Weather.objects.count())
        self.assertEqual('San Jose', Weather.objects.retrieve_weather_object(city='San Jose', state='CA').city)
        self.assertEqual(1, Weather.objects.count())

    def test_retreive_non_existing_weather(self):
        print('running 2nd test')
        self.assertEqual(1, Weather.objects.count())
        self.assertEqual('San Diego', Weather.objects.retrieve_weather_object(city='San Diego', state='CA').city)
        self.assertEqual(2, Weather.objects.count())

    def tearDown(self):
        print('happens after every test')

class BulkWeatherRetrievalTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Weather.objects.create(city='Boston', state='MA')
        Weather.objects.create(city='Richmond', state='VA')
        Weather.objects.create(city='Sacramento', state='CA')

    def test_bulk_retrieve_existing_weather_all_exist(self):
        print('running 3rd test')
        self.assertEqual(3, Weather.objects.count())
        weathers = Weather.objects.retrieve_weather_objects([('Boston', 'MA'), ('Richmond', 'VA'), ('Sacramento', 'CA')])
        self.asesrtEqual('Boston', weather[0].city)
        self.asesrtEqual('Richmond', weather[1].city)
        self.assertEqual('Sacramento', weather[2].city)
        self.assertEqual(3, Weather.objects.count())

    def test_bulk_retrieve_existing_weather_some_exist(self):
        pass

    def test_bulk_retrieve_existing_weather_none_exist(self):
        pass





