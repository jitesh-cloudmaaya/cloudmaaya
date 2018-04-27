# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import requests
import datetime

from django.db import models
from django.conf import settings

class WeatherManager(models.Manager):
    def retrieve_weather_object(self, city, state):
        """
        Returns a weather object based on a city and state pair from the database.
        If it does not exist, creates it. Returns None if no weather object could be created.

        args
        city - a string representing a city name
        state - a string representing the state abbreviation
        """
        # trim potential whitespace
        try:
            city = city.strip()
            state = state.strip()

            # map abbrevations to full state names, where possible
            us_state_abbrev = {
            'alabama': 'AL',
            'alaska': 'AK',
            'arizona': 'AZ',
            'arkansas': 'AR',
            'california': 'CA',
            'colorado': 'CO',
            'connecticut': 'CT',
            'delaware': 'DE',
            'florida': 'FL',
            'georgia': 'GA',
            'hawaii': 'HI',
            'idaho': 'ID',
            'illinois': 'IL',
            'indiana': 'IN',
            'iowa': 'IA',
            'kansas': 'KS',
            'kentucky': 'KY',
            'louisiana': 'LA',
            'maine': 'ME',
            'maryland': 'MD',
            'massachusetts': 'MA',
            'michigan': 'MI',
            'minnesota': 'MN',
            'mississippi': 'MS',
            'missouri': 'MO',
            'montana': 'MT',
            'nebraska': 'NE',
            'nevada': 'NV',
            'new hampshire': 'NH',
            'new jersey': 'NJ',
            'new mexico': 'NM',
            'new york': 'NY',
            'north carolina': 'NC',
            'north dakota': 'ND',
            'ohio': 'OH',
            'oklahoma': 'OK',
            'oregon': 'OR',
            'pennsylvania': 'PA',
            'rhode island': 'RI',
            'south carolina': 'SC',
            'south dakota': 'SD',
            'tennessee': 'TN',
            'texas': 'TX',
            'utah': 'UT',
            'vermont': 'VT',
            'virginia': 'VA',
            'washington': 'WA',
            'west virginia': 'WV',
            'wisconsin': 'WI',
            'wyoming': 'WY',
            'district of columbia': 'DC',
            }

            state = us_state_abbrev.pop(state.lower(), state) # convert name to abbrev if in dict, else use what should be 2 letter state abbr
        except:
            city = ''
            state = ''

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

    _spring_temperature_average = models.FloatField(default=None, null=True, db_column='spring_temperature_average')
    _spring_temperature_high = models.FloatField(default=None, null=True, db_column='spring_temperature_high')
    _spring_temperature_low = models.FloatField(default=None, null=True, db_column='spring_temperature_low')
    _spring_precipitation = models.FloatField(default=None, null=True, db_column='spring_precipitation')
    _spring_snowfall = models.FloatField(default=None, null=True, db_column='spring_snowfall')
    _spring_wind = models.FloatField(default=None, null=True, db_column='spring_wind')
    _spring_sun = models.FloatField(default=None, null=True, db_column='spring_sun')

    _summer_temperature_average = models.FloatField(default=None, null=True, db_column='summer_temperature_average')
    _summer_temperature_high = models.FloatField(default=None, null=True, db_column='summer_temperature_high')
    _summer_temperature_low = models.FloatField(default=None, null=True, db_column='summer_temperature_low')
    _summer_precipitation = models.FloatField(default=None, null=True, db_column='summer_precipitation')
    _summer_snowfall = models.FloatField(default=None, null=True, db_column='summer_snowfall')
    _summer_wind = models.FloatField(default=None, null=True, db_column='summer_wind')
    _summer_sun = models.FloatField(default=None, null=True, db_column='summer_sun')

    _autumn_temperature_average = models.FloatField(default=None, null=True, db_column='autumn_temperature_average')
    _autumn_temperature_high = models.FloatField(default=None, null=True, db_column='autumn_temperature_high')
    _autumn_temperature_low = models.FloatField(default=None, null=True, db_column='autumn_temperature_low')
    _autumn_precipitation = models.FloatField(default=None, null=True, db_column='autumn_precipitation')
    _autumn_snowfall = models.FloatField(default=None, null=True, db_column='autumn_snowfall')
    _autumn_wind = models.FloatField(default=None, null=True, db_column='autumn_wind')
    _autumn_sun = models.FloatField(default=None, null=True, db_column='autumn_sun')

    _winter_temperature_average = models.FloatField(default=None, null=True, db_column='winter_temperature_average')
    _winter_temperature_high = models.FloatField(default=None, null=True, db_column='winter_temperature_high')
    _winter_temperature_low = models.FloatField(default=None, null=True, db_column='winter_temperature_low')
    _winter_precipitation = models.FloatField(default=None, null=True, db_column='winter_precipitation')
    _winter_snowfall = models.FloatField(default=None, null=True, db_column='winter_snowfall')
    _winter_wind = models.FloatField(default=None, null=True, db_column='winter_wind')
    _winter_sun = models.FloatField(default=None, null=True, db_column='winter_sun')

    objects = WeatherManager()

    # spring attribute property methods
    @property
    def spring_temperature_average(self):
        return self.model_field_helper(self._spring_temperature_average)
    @property
    def spring_temperature_high(self):
        return self.model_field_helper(self._spring_temperature_high)
    @property
    def spring_temperature_low(self):
        return self.model_field_helper(self._spring_temperature_low)
    @property
    def spring_precipitation(self):
        return self.model_field_helper(self._spring_precipitation)
    @property
    def spring_snowfall(self):
        return self.model_field_helper(self._spring_snowfall)
    @property
    def spring_wind(self):
        return self.model_field_helper(self._spring_wind)
    @property
    def spring_sun(self):
        return self.model_field_helper(self._spring_sun)

    # summer attribute property methods
    @property
    def summer_temperature_average(self):
        return self.model_field_helper(self._summer_temperature_average)
    @property
    def summer_temperature_high(self):
        return self.model_field_helper(self._summer_temperature_high)
    @property
    def summer_temperature_low(self):
        return self.model_field_helper(self._summer_temperature_low)
    @property
    def summer_precipitation(self):
        return self.model_field_helper(self._summer_precipitation)
    @property
    def summer_snowfall(self):
        return self.model_field_helper(self._summer_snowfall)
    @property
    def summer_wind(self):
        return self.model_field_helper(self._summer_wind)
    @property
    def summer_sun(self):
        return self.model_field_helper(self._summer_sun)

    # autumn attribute property methods
    @property
    def autumn_temperature_average(self):
        return self.model_field_helper(self._autumn_temperature_average)
    @property
    def autumn_temperature_high(self):
        return self.model_field_helper(self._autumn_temperature_high)
    @property
    def autumn_temperature_low(self):
        return self.model_field_helper(self._autumn_temperature_low)
    @property
    def autumn_precipitation(self):
        return self.model_field_helper(self._autumn_precipitation)
    @property
    def autumn_snowfall(self):
        return self.model_field_helper(self._autumn_snowfall)
    @property
    def autumn_wind(self):
        return self.model_field_helper(self._autumn_wind)
    @property
    def autumn_sun(self):
        return self.model_field_helper(self._autumn_sun)

    # winter attribute property methods
    @property
    def winter_temperature_average(self):
        return self.model_field_helper(self._winter_temperature_average)
    @property
    def winter_temperature_high(self):
        return self.model_field_helper(self._winter_temperature_high)
    @property
    def winter_temperature_low(self):
        return self.model_field_helper(self._winter_temperature_low)
    @property
    def winter_precipitation(self):
        return self.model_field_helper(self._winter_precipitation)
    @property
    def winter_snowfall(self):
        return self.model_field_helper(self._winter_snowfall)
    @property
    def winter_wind(self):
        return self.model_field_helper(self._winter_wind)
    @property
    def winter_sun(self):
        return self.model_field_helper(self._winter_sun)

    @property
    def spring_icon(self):
        sunny = self._spring_sun >= 50
        windy = self._spring_wind >= 8
        gusty = self._spring_wind > 15
        rainy = self._spring_precipitation > 3
        snowy = self._spring_snowfall > 2
        return self.select_icon(sunny, windy, gusty, rainy, snowy)
    
    @property
    def summer_icon(self):
        sunny = self._summer_sun >= 50
        windy = self._summer_wind >= 8
        gusty = self._summer_wind > 15
        rainy = self._summer_precipitation > 3
        snowy = self._summer_snowfall > 2
        return self.select_icon(sunny, windy, gusty, rainy, snowy)

    @property
    def autumn_icon(self):
        sunny = self._autumn_sun >= 50
        windy = self._autumn_wind >= 8
        gusty = self._autumn_wind > 15
        rainy = self._autumn_precipitation > 3
        snowy = self._autumn_snowfall > 2
        return self.select_icon(sunny, windy, gusty, rainy, snowy)

    @property
    def winter_icon(self):
        sunny = self._winter_sun >= 50
        windy = self._winter_wind >= 8
        gusty = self._winter_wind > 15
        rainy = self._winter_precipitation > 3
        snowy = self._winter_snowfall > 2
        return self.select_icon(sunny, windy, gusty, rainy, snowy)

    def model_field_helper(self, model_field):
        """
        Helper method for newly defined properties to handle null values
        Args:
          model_field (float): The Weather object's model FloatField value.

        Returns:
          float: Returns the float value that is passed to the method.
          str: Returns the string '--' as a replacement for emtpy values for display
          on the front end.
        """
        if model_field:
            print model_field
            return model_field
        return '--'

    def select_icon(self, sunny, windy, gusty, rainy, snowy):
        """
        Helper method that takes in boolean weather conditions to determine which icon to use.
        Args:
          sunny (bool): A boolean determining whether the weather is considered sunny.
          windy (bool): A boolean determining whether the weather is considered windy.
          gusty (bool): A boolean determining whether the weather is considered gusty.
          rainy (bool): A boolean determining whether the weather is considered rainy.
          snowy (bool): A boolean determining whether the weather is considered snowy.

        Returns:
          str: The class name string to use on the front end. Corresponds to an icon class.
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
                            self._spring_temperature_average = value
                        elif attr == 'TMAX':
                            self._spring_temperature_high = value
                        elif attr == 'TMIN':
                            self._spring_temperature_low = value
                        elif attr == 'SNOW':
                            self._spring_snowfall = value
                        elif attr == 'PRCP':
                            self._spring_precipitation = value
                        elif attr == 'AWND':
                            self._spring_wind = value
                        elif attr == 'PSUN':
                            self._spring_sun = value
                if season == 'summer':
                    for attr, value in values.items():
                        if attr == 'TAVG':
                            self._summer_temperature_average = value
                        elif attr == 'TMAX':
                            self._summer_temperature_high = value
                        elif attr == 'TMIN':
                            self._summer_temperature_low = value
                        elif attr == 'SNOW':
                            self._summer_snowfall = value
                        elif attr == 'PRCP':
                            self._summer_precipitation = value
                        elif attr == 'AWND':
                            self._summer_wind = value
                        elif attr == 'PSUN':
                            self._summer_sun = value
                if season == 'autumn':
                    for attr, value in values.items():
                        if attr == 'TAVG':
                            self._autumn_temperature_average = value
                        elif attr == 'TMAX':
                            self._autumn_temperature_high = value
                        elif attr == 'TMIN':
                            self._autumn_temperature_low = value
                        elif attr == 'SNOW':
                            self._autumn_snowfall = value
                        elif attr == 'PRCP':
                            self._autumn_precipitation = value
                        elif attr == 'AWND':
                            self._autumn_wind = value
                        elif attr == 'PSUN':
                            self._autumn_sun = value
                if season == 'winter':
                    for attr, value in values.items():
                        if attr == 'TAVG':
                            self._winter_temperature_average = value
                        elif attr == 'TMAX':
                            self._winter_temperature_high = value
                        elif attr == 'TMIN':
                            self._winter_temperature_low = value
                        elif attr == 'SNOW':
                            self._winter_snowfall = value
                        elif attr == 'PRCP':
                            self._winter_precipitation = value
                        elif attr == 'AWND':
                            self._winter_wind = value
                        elif attr == 'PSUN':
                            self._winter_sun = value

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

        headers = {'token': settings.NOAA_TOKEN}

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






