# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import requests

import datetime # temp?

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


### BEGIN LOGIC TO ASSIGN LABELS/values

# I would think we want values, labels, and the icon to use
# e.g. temp = x, prcp = y, label is 'warm but x', icon is 'erikflowers.css'


# cases 

# temperature, hot vs cold




### END LOGIC TO ASSIGN LABELS/values


class Weather(models.Model):
    id = models.AutoField(primary_key=True) # added by Django by default?
    # id = models.BigAutoField(primary_key=True) # go with bigger?
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    spring_temperature = models.CharField(max_length=15, default='', blank=True)
    spring_precipitation = models.CharField(max_length=15, default='', blank=True)
    spring_snowfall = models.CharField(max_length=15, default='', blank=True)
    spring_wind = models.CharField(max_length=15, default='', blank=True)
    spring_sun = models.CharField(max_length=15, default='', blank=True)

    # first guesses at description and icon fields for Weather
    
    # spring_description = models.CharField(max_length=255, default='', blank=True)
    # spring_icon = models.CharField(max_length=255, default='', blank=True)

    # summer_description = models.CharField(max_length=255, default='', blank=True)
    # summer_icon = models.CharField(max_length=255, default='', blank=True)

    # autumn_description = models.CharField(max_length=255, default='', blank=True)
    # autumn_icon = models.CharField(max_length=255, default='', blank=True)

    # winter_description = models.CharField(max_length=255, default='', blank=True)
    # winter_icon = models.CharField(max_length=255, default='', blank=True)

    # end field guesses

    summer_temperature = models.CharField(max_length=15, default='', blank=True)
    summer_precipitation = models.CharField(max_length=15, default='', blank=True)
    summer_snowfall = models.CharField(max_length=15, default='', blank=True)
    summer_wind = models.CharField(max_length=15, default='', blank=True)
    summer_sun = models.CharField(max_length=15, default='', blank=True)

    autumn_temperature = models.CharField(max_length=15, default='', blank=True)
    autumn_precipitation = models.CharField(max_length=15, default='', blank=True)
    autumn_snowfall = models.CharField(max_length=15, default='', blank=True)
    autumn_wind = models.CharField(max_length=15, default='', blank=True)
    autumn_sun = models.CharField(max_length=15, default='', blank=True)

    winter_temperature = models.CharField(max_length=15, default='', blank=True)
    winter_precipitation = models.CharField(max_length=15, default='', blank=True)
    winter_snowfall = models.CharField(max_length=15, default='', blank=True)
    winter_wind = models.CharField(max_length=15, default='', blank=True)
    winter_sun = models.CharField(max_length=15, default='', blank=True)

    objects = WeatherManager()

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


        # current input can look like
        # {'spring': {'temp': 'cool', 'precip': 'rainy', 'snow': 'not snowy', 'wind': 'breezy', 'sun': None},
        #  'summer': {'temp', 'precip', 'snow', 'wind', 'sun'},
        #  'autumn': {'temp', 'precip', 'snow', 'wind', 'sun'},
        #  'winter': {'temp', 'precip', 'snow', 'wind', 'sun'},}

        ### BEGIN NEW LABEL ASSIGNMENT




        # season_weather = self.get_weather(self.city, self.state, data_year, data_year) # start and end year currently the same


        # if season_weather:
        #     for season in season_weather:
        #         if season == 'spring':
        #             attrs = season_weather[season]

        #             temperature_label = ''
        #             additional_labels = []

        #             seen = set() # track which attrs have been looped over for this property:
        #             # always include temp if able, one of snowy or rainy if present, additional properties until len == 2

        #             for attr in attrs:
        #                 if attr == 'TAVG':
        #                     temperature_label = attrs[attr]
        #                 elif attr == 'PRCP':

        #                     pass
        #                 elif attr == 'SNOW':
        #                     pass
        #                 else:
        #                     additional_labels.append(attrs[attr])

        #             spring_description = temperature_label
        #             spring_icon = choose_icon(spring_description)


        #         elif season == 'summer':
        #             pass
        #         elif season == 'autumn':
        #             pass
        #         elif season == 'winter':
        #             pass


        # temperature_label = 
        # additional_labels = # should be no longer than 2 items
        # description = temperature_label
        # for label in additional_labels:
        #     description += label + ', '
        # description[:-2] # remove trailing ', '





        ### END NEW LABEL ASSIGNMENT

        # weather label assignment
        season_weather = self.get_weather(self.city, self.state, data_year, data_year) # start and end year currently the same
        if season_weather:
            for season, values in season_weather.items():
                if season == 'spring':
                    for attr, label in values.items():
                        if attr == 'TAVG':
                            self.spring_temperature = label
                        elif attr == 'PRCP':
                            self.spring_precipitation = label
                        elif attr == 'SNOW':
                            self.spring_snowfall = label
                        elif attr == 'AWND':
                            self.spring_wind = label
                        elif attr == 'PSUN':
                            self.spring_sunshine = label
                elif season == 'summer':
                    for attr, label in values.items():
                        if attr == 'TAVG':
                            self.summer_temperature = label
                        elif attr == 'PRCP':
                            self.summer_precipitation = label
                        elif attr == 'SNOW':
                            self.summer_snowfall = label
                        elif attr == 'AWND':
                            self.summer_wind = label
                        elif attr == 'PSUN':
                            self.summer_sunshine = label
                elif season == 'autumn':
                    for attr, label in values.items():
                        if attr == 'TAVG':
                            self.autumn_temperature = label
                        elif attr == 'PRCP':
                            self.autumn_precipitation = label
                        elif attr == 'SNOW':
                            self.autumn_snowfall = label
                        elif attr == 'AWND':
                            self.autumn_wind = label
                        elif attr == 'PSUN':
                            self.autumn_sunshine = label
                elif season == 'winter':
                    for attr, label in values.items():
                        if attr == 'TAVG':
                            self.winter_temperature = label
                        elif attr == 'PRCP':
                            self.winter_precipitation = label
                        elif attr == 'SNOW':
                            self.winter_snowfall = label
                        elif attr == 'AWND':
                            self.winter_wind = label
                        elif attr == 'PSUN':
                            self.winter_sunshine = label

            super(Weather, self).save(*args, **kwargs)


    def choose_icon(description):
        """
        Takes a seasonal description ('warm, rainy, and windy') and returns the appropriate icon from
        erikflowers to use.
        """
        icon_label = None


        return icon_label

    # save helpers
    # change method to accept year parameter
    def get_weather(self, city, state, start_year, end_year):
        """
        Accesses the NOAA API to get the available weather data for the city and state provided.

        args
        city -- a string denoting city name
        state -- a string denoting the state's abbreviation
        """

        START_MONTH = None
        END_MONTH = None

        zip_codes = self.get_zip_codes(city, state)

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

        # maybe change to iteratve over season_weather?
        for season in season_weather:
            for attr in season_weather[season]:
                val = season_weather[season][attr]
                if val != '':
                    if attr == 'TAVG':
                        if val < 60:
                            season_weather[season][attr] = 'cold'
                        elif val <= 80 and val > 60:
                            season_weather[season][attr] = 'cool'
                        elif val < 100 and val > 80:
                            season_weather[season][attr] = 'warm'
                        else:
                            season_weather[season][attr] = 'hot'
                    elif attr == 'PRCP':
                        if val > 3:
                            season_weather[season][attr] = 'rainy'
                        else:
                            season_weather[season][attr] = 'dry'
                    elif attr == 'SNOW':
                        if val > 2:
                            season_weather[season][attr] = 'snowy'
                        else:
                            season_weather[season][attr] = 'not snowy'
                    elif attr == 'AWND':
                        # if val >= 8:
                        #     season_weather[season][attr] = 'windy'
                        # else:
                        #     season_weather[season][attr] = 'calm'
                        if val >= 15:
                            season_weather[season][attr] = 'windy'
                        elif val >= 8 and val < 15:
                            season_weather[season][attr] = 'breezy'
                        else:
                            season_weather[season][attr] = 'calm'
                    elif attr == 'PSUN':
                        if val >= 95:
                            season_weather[season][attr] = 'clear'
                        elif val >= 75 and val < 95:
                            season_weather[season][attr] = 'sunny'
                        elif val >= 50 and val < 75:
                            season_weather[season][attr] = 'mostly sunny' # partly cloudy
                        elif val >= 13 and val < 50:
                            season_weather[season][attr] = 'partly sunny' # mostly cloudy
                        else:
                            season_weather[season][attr] = 'cloudy' # or overcast
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



