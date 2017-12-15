# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import requests
import datetime

from django.db import models

class WeatherManager(models.Manager):
    def retrieve_weather_object(self, city, state):
        """
        Returns a weather object based on a city and state pair from the database.
        If it does not exist, creates it. Returns None if no weather object could be created.

        args
        city - a string representing a city name
        state - a string representing the state abbreviation
        """
        weather = self.get_or_create(city=city, state=state)[0] # get_or_create returns an obj, created_bool tuple
        if weather.id:
            # if data not recent enough
            if (datetime.datetime.now().year - 1) > weather.last_modified.year: # for now, check if the year prior the current year has 12 monthly summaries and is more recent than the last modified
                weather.save()

            return weather

    def retrieve_weather_objects(self, cities_states):
        """
        Given a collection of (city, state) pairs, returns the Weather object associated with each,
        creating it if it does not exist.

        args
        cities_states -- a list of ('city', 'state') tuples
        """
        results = []
        for city, state in cities_states:
            results.append(self.retrieve_weather_object(city, state))
        return results


class Weather(models.Model):
    id = models.AutoField(primary_key=True) # added by Django by default?
    # id = models.BigAutoField(primary_key=True) # go with bigger?
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    spring_temperature = models.FloatField(default=0)
    spring_precipitation = models.FloatField(default=0)
    spring_snowfall = models.FloatField(default=0)
    spring_wind = models.FloatField(default=0)
    spring_sun = models.FloatField(default=0)

    # first guesses at description and icon fields for Weather
    # icon fieldtype is a guess    
    spring_description = models.CharField(max_length=255, default='', blank=True)
    spring_icon = models.CharField(max_length=255, default='', blank=True)

    summer_description = models.CharField(max_length=255, default='', blank=True)
    summer_icon = models.CharField(max_length=255, default='', blank=True)

    autumn_description = models.CharField(max_length=255, default='', blank=True)
    autumn_icon = models.CharField(max_length=255, default='', blank=True)

    winter_description = models.CharField(max_length=255, default='', blank=True)
    winter_icon = models.CharField(max_length=255, default='', blank=True)

    summer_temperature = models.FloatField(default=0)
    summer_precipitation = models.FloatField(default=0)
    summer_snowfall = models.FloatField(default=0)
    summer_wind = models.FloatField(default=0)
    summer_sun = models.FloatField(default=0)

    autumn_temperature = models.FloatField(default=0)
    autumn_precipitation = models.FloatField(default=0)
    autumn_snowfall = models.FloatField(default=0)
    autumn_wind = models.FloatField(default=0)
    autumn_sun = models.FloatField(default=0)

    winter_temperature = models.FloatField(default=0)
    winter_precipitation = models.FloatField(default=0)
    winter_snowfall = models.FloatField(default=0)
    winter_wind = models.FloatField(default=0)
    winter_sun = models.FloatField(default=0)

    objects = WeatherManager()

    @property
    def icon(self):
        "Returns the id of the appropriate icon to display based on snow, precipitation, wind, and sunshine."
        season = 'summer'
        icon_id = 'wi-day-cloudy' # default to zero sunshine state?

        # make sure fields are initialized to 0 rather than None for comparison or otherwise handle
        if self.summer_sun >= 50:
            icon_id = 'wi-day-sunny'
        if self.summer_wind >= 8:
            icon_id = 'wi-day-cloudy-windy'
        if self.summer_wind > 15:
            icon_id = 'wi-day-cloudy-gusts'
        if self.summer_precipitation > 3:
            icon_id = 'wi-day-rain'
        if self.summer_snowfall > 2:
            icon_id = 'wi-day-snow'
        return icon_id



        # if season == 'summer':
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
        # elif season == 'spring':
        #     pass
        # elif season == 'autumn':
        #     pass
        # elif season == 'winter':
        #     pass
        
        # return icon_id



    # @property
    # def winter_icon(self):
    #     icon_id = 'wi-day-cloudy'
    #     if self.winter_sun >= 50:
    #         icon_id = 'wi-day-sunny'
    #     if self.winter_wind >= 8:
    #         icon_id = 'wi-day-cloudy-windy'
    #     if self.winter_wind > 15:
    #         icon_id = 'wi-day-cloudy-gusts'
    #     if self.winter_precipitation > 3:
    #         icon_id = 'wi-day-rain'
    #     if self.winter_snowfall > 2:
    #         icon_id = 'wi-day-snow'

    #     return icon_id


    class Meta:
        unique_together = (('city', 'state'),)
        # index_together = [
        #     ['city', 'state'],
        # ]

    def save(self, *args, **kwargs):
        # capitalize city name and state abbreviation properly
        self.city = self.city.lower().title()
        self.state = self.state.upper()

        data_year = datetime.datetime.now().year - 1
        data_year = str(data_year)

        # using weather data, fill model attributes
        season_weather = self.get_weather(data_year, data_year) # start and end year currently the same
        if season_weather:
            for season, values in season_weather.items():
                if season == 'spring':
                    for attr, value in values.items():
                        if attr == 'TAVG':
                            self.spring_temperature = value
                        elif attr == 'SNOW':
                            self.spring_snowfall = value
                        elif attr == 'PRCP':
                            self.spring_precipitation = value
                        elif attr == 'AWND':
                            self.spring_wind = value
                        elif attr == 'PSUN':
                            self.spring_sunshine = value
                if season == 'summer':
                    for attr, value in values.items():
                        if attr == 'TAVG':
                            self.summer_temperature = value
                        elif attr == 'SNOW':
                            self.summer_snowfall = value
                        elif attr == 'PRCP':
                            self.summer_precipitation = value
                        elif attr == 'AWND':
                            self.summer_wind = value
                        elif attr == 'PSUN':
                            self.summer_sunshine = value
                if season == 'autumn':
                    for attr, value in values.items():
                        if attr == 'TAVG':
                            self.autumn_temperature = value
                        elif attr == 'SNOW':
                            self.autumn_snowfall = value
                        elif attr == 'PRCP':
                            self.autumn_precipitation = value
                        elif attr == 'AWND':
                            self.autumn_wind = value
                        elif attr == 'PSUN':
                            self.autumn_sunshine = value
                if season == 'winter':
                    for attr, value in values.items():
                        if attr == 'TAVG':
                            self.winter_temperature = value
                        elif attr == 'SNOW':
                            self.winter_snowfall = value
                        elif attr == 'PRCP':
                            self.winter_precipitation = value
                        elif attr == 'AWND':
                            self.winter_wind = value
                        elif attr == 'PSUN':
                            self.winter_sunshine = value

            super(Weather, self).save(*args, **kwargs)

    # save helpers
    # change method to accept year parameter
    def get_weather(self, start_year, end_year):
        """
        Accesses the NOAA API to get the available weather data for the city and state provided.

        args
        city -- a string denoting city name
        state -- a string denoting the state's abbreviation
        """

        START_MONTH = None
        END_MONTH = None

        zip_codes = self.get_zip_codes(self.city, self.state)

        url = 'https://www.ncdc.noaa.gov/cdo-web/api/v2/data?datasetid=GSOM'
        try:
            # refine how to limit zip code count
            for zip_code in zip_codes[:180]:
                url += '&locationid=ZIP:' + zip_code
        except:
            # print('city, state pair produced no zip codes!')
            return
            
        url += '&startdate=' + start_year + '-01-01&enddate=' + end_year + '-12-31'
        url += '&datatypeid=PSUN' # Daily percent of possible sunshine for the period
        url += '&datatypeid=PRCP' # rainfall in in
        url += '&datatypeid=SNOW' # snowfall in in
        url += '&datatypeid=TAVG' # temperature average in fahrenheit
        url += '&datatypeid=AWND' # average wind speed in mph
        url += '&limit=1000'
        url += '&units=standard' # converts to standard
        url += '&includemetadata=false' # impove response time by preventing calc of result metadata    

        headers = {'token': 'YdgPMhahlBcRshMkgsmDaoFlvAFcjwnr'}


        try:
            response = requests.get(url, headers = headers)
            response = response.json()            
            results = response['results']
        except:
            # print('no noaa data found for zip codes')
            return

        # construct season_weather dictionary from response
        season_weather = {
            'spring': {'PRCP': '', 'SNOW': '', 'TAVG': '', 'PSUN': '', 'AWND': ''},
            'summer': {'PRCP': '', 'SNOW': '', 'TAVG': '', 'PSUN': '', 'AWND': ''},
            'autumn': {'PRCP': '', 'SNOW': '', 'TAVG': '', 'PSUN': '', 'AWND': ''},
            'winter': {'PRCP': '', 'SNOW': '', 'TAVG': '', 'PSUN': '', 'AWND': ''}
        }
        for datum in results:
            date = datum['date']
            month = date[5:7]
            datatype = datum['datatype'] # e.g. 'PRCP' or 'TAVG'
            value = datum['value']
            season = None

            if month == '03' or month == '04' or month == '05':
                season = 'spring'
            elif month == '06' or month == '07' or month == '08':
                season = 'summer'
            elif month == '09' or month == '10' or month == '11':
                season = 'autumn'
            elif month == '12' or month == '01' or month == '02':
                season = 'winter'
            
            try:
                if season_weather[season][datatype]:
                    season_weather[season][datatype].append(value)
                else:
                    season_weather[season][datatype] = [value]
            except:
                # print('data error')
                return

        for season in season_weather:
            for attr in season_weather[season]:
                if season_weather[season][attr]:
                    season_weather[season][attr] = sum(season_weather[season][attr]) / len(season_weather[season][attr])

        return season_weather


    def get_zip_codes(self, comp_city, comp_state):
        """
        Given a city and state combination, returns the ZIP code(s).

        args:
        comp_city -- a string denoting city name
        comp_state -- a string denoting the state's abbreviation
        """
        if not comp_city or not comp_state:
            # print('cannot leave either argument blank!')
            return
        url = 'http://api.zippopotam.us/us/' + comp_state + '/' + comp_city
        try:
            response = requests.get(url)
            response = response.json()
            places = response['places']
        except:
            # print('invalid city/state combination!')
            return

        zip_codes = []
        for place in places:
            zip_codes.append(place['post code'])
        return zip_codes

    def __str__(self):
        return self.city + ', ' + self.state



