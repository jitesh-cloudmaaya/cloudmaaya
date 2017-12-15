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
            # check if the year prior the current year has 12 monthly summaries and is more recent than the last modified
            if (datetime.datetime.now().year - 1) > weather.last_modified.year:
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
    id = models.AutoField(primary_key=True)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    spring_temperature_average = models.FloatField(default=None, null=True)
    spring_temperature_high = models.FloatField(default=None, null=True)
    spring_temperature_low = models.FloatField(default=None, null=True)
    spring_precipitation = models.FloatField(default=0.0)
    spring_snowfall = models.FloatField(default=0.0)
    spring_wind = models.FloatField(default=0.0)
    spring_sun = models.FloatField(default=0.0)

    summer_temperature_average = models.FloatField(default=None, null=True)
    summer_temperature_high = models.FloatField(default=None, null=True)
    summer_temperature_low = models.FloatField(default=None, null=True)
    summer_precipitation = models.FloatField(default=0.0)
    summer_snowfall = models.FloatField(default=0.0)
    summer_wind = models.FloatField(default=0.0)
    summer_sun = models.FloatField(default=0.0)

    autumn_temperature_average = models.FloatField(default=None, null=True)
    autumn_temperature_high = models.FloatField(default=None, null=True)
    autumn_temperature_low = models.FloatField(default=None, null=True)
    autumn_precipitation = models.FloatField(default=0.0)
    autumn_snowfall = models.FloatField(default=0.0)
    autumn_wind = models.FloatField(default=0.0)
    autumn_sun = models.FloatField(default=0.0)

    winter_temperature_average = models.FloatField(default=None, null=True)
    winter_temperature_high = models.FloatField(default=None, null=True)
    winter_temperature_low = models.FloatField(default=None, null=True)
    winter_precipitation = models.FloatField(default=0.0)
    winter_snowfall = models.FloatField(default=0.0)
    winter_wind = models.FloatField(default=0.0)
    winter_sun = models.FloatField(default=0.0)

    objects = WeatherManager()

    @property
    def spring_icon(self):
        sunny = self.spring_sun >= 50
        windy = self.spring_wind >= 8
        gusty = self.spring_wind > 15
        rainy = self.spring_precipitation > 3
        snowy = self.spring_snowfall > 2
        return self.select_icon(sunny, windy, gusty, rainy, snowy)
    
    @property
    def summer_icon(self):
        sunny = self.summer_sun >= 50
        windy = self.summer_wind >= 8
        gusty = self.summer_wind > 15
        rainy = self.summer_precipitation > 3
        snowy = self.summer_snowfall > 2
        return self.select_icon(sunny, windy, gusty, rainy, snowy)

    @property
    def autumn_icon(self):
        sunny = self.autumn_sun >= 50
        windy = self.autumn_wind >= 8
        gusty = self.autumn_wind > 15
        rainy = self.autumn_precipitation > 3
        snowy = self.autumn_snowfall > 2
        return self.select_icon(sunny, windy, gusty, rainy, snowy)

    @property
    def winter_icon(self):
        sunny = self.winter_sun >= 50
        windy = self.winter_wind >= 8
        gusty = self.winter_wind > 15
        rainy = self.winter_precipitation > 3
        snowy = self.winter_snowfall > 2
        return self.select_icon(sunny, windy, gusty, rainy, snowy)

    def select_icon(self, sunny, windy, gusty, rainy, snowy):
        """
        Helper method that takes in boolean weather conditions to determine which icon to use.
        """
        icon_id = 'wi-day-cloudy' # default
        if sunny:
            icon_id = 'wi-day-sunny'
        if windy:
            if not sunny:
                icon_id = 'wi-day-cloudy-windy'
            else:
                icon_id = 'wi-day-light-wind'
        if gusty:
            if not sunny:
                icon_id = 'wi-day-cloudy-gusts'
            else:
                icon_id = 'wi-day-windy'
        if rainy:
            if windy:
                icon_id = 'wi-day-rain-wind'
            else:
                icon_id = 'wi-day-rain'
        if snowy:
            if windy:
                icon_id = 'wi-day-snow-wind'
            else:
                icon_id = 'wi-day-snow'
        return icon_id

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
        season_weather = self.get_weather(data_year) # start and end year currently the same
        if season_weather:
            for season, values in season_weather.items():
                if season == 'spring':
                    for attr, value in values.items():
                        if attr == 'TAVG':
                            self.spring_temperature_average = value
                        elif attr == 'TMAX':
                            self.spring_temperature_high = value
                        elif attr == 'TMIN':
                            self.spring_temperature_low = value
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
                            self.summer_temperature_average = value
                        elif attr == 'TMAX':
                            self.summer_temperature_high = value
                        elif attr == 'TMIN':
                            self.summer_temperature_low = value
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
                            self.autumn_temperature_average = value
                        elif attr == 'TMAX':
                            self.autumn_temperature_high = value
                        elif attr == 'TMIN':
                            self.autumn_temperature_low = value
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
                            self.winter_temperature_average = value
                        elif attr == 'TMAX':
                            self.winter_temperature_high = value
                        elif attr == 'TMIN':
                            self.winter_temperature_low = value
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
    def get_weather(self, year):
        """
        Accesses the NOAA API to get the available weather data for the city and state provided.

        args
        year -- string denoting the year to get reports from
        """

        # START_MONTH = None
        # END_MONTH = None

        zip_codes = self.get_zip_codes(self.city, self.state)

        url = 'https://www.ncdc.noaa.gov/cdo-web/api/v2/data?datasetid=GSOM'
        try:
            for zip_code in zip_codes[:150]:
                url += '&locationid=ZIP:' + zip_code
        except:
            return
            
        url += '&startdate=' + year + '-01-01&enddate=' + year + '-12-31'
        url += '&datatypeid=PSUN' # Daily percent of possible sunshine for the period
        url += '&datatypeid=PRCP' # rainfall in in
        url += '&datatypeid=SNOW' # snowfall in in
        url += '&datatypeid=TAVG' # temperature average in fahrenheit
        url += '&datatypeid=TMAX' # maximum temperature in fahrenheit
        url += '&datatypeid=TMIN' # minimum temperature in fahrenheit
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
            return

        # construct season_weather dictionary from response
        season_weather = {
            'spring': {'TAVG': None, 'TMAX': None, 'TMIN': None, 'SNOW': 0.0, 'PRCP': 0.0, 'AWND': 0.0, 'PSUN': 0.0},
            'summer': {'TAVG': None, 'TMAX': None, 'TMIN': None, 'SNOW': 0.0, 'PRCP': 0.0, 'AWND': 0.0, 'PSUN': 0.0},
            'autumn': {'TAVG': None, 'TMAX': None, 'TMIN': None, 'SNOW': 0.0, 'PRCP': 0.0, 'AWND': 0.0, 'PSUN': 0.0},
            'winter': {'TAVG': None, 'TMAX': None, 'TMIN': None, 'SNOW': 0.0, 'PRCP': 0.0, 'AWND': 0.0, 'PSUN': 0.0}
        }
        for datum in results:
            date = datum['date']
            month = date[5:7]
            datatype = datum['datatype'] # e.g. 'PRCP' or 'TAVG'
            value = datum['value']
            season = None

            # seasons as defined by meterological convention in the northern hemisphere 
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
                return

        for season in season_weather:
            for attr in season_weather[season]:
                if season_weather[season][attr]:
                    season_weather[season][attr] = float(sum(season_weather[season][attr]) / len(season_weather[season][attr]))

        return season_weather

    def get_zip_codes(self, city, state):
        """
        Given a city and state combination, returns the ZIP code(s).

        args:
        city -- a string denoting city name
        state -- a string denoting the state's abbreviation
        """
        if not city or not state:
            return
        url = 'http://api.zippopotam.us/us/' + state + '/' + city
        try:
            response = requests.get(url)
            response = response.json()
            places = response['places']
        except:
            return

        zip_codes = []
        for place in places:
            zip_codes.append(place['post code'])
        if zip_codes:
            return zip_codes
        return

    def __str__(self):
        return self.city + ', ' + self.state






