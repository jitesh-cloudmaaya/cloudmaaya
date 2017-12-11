import requests
import time
# import json


# implementation leveraging zippopotam.us
def get_zip_codes(comp_city, comp_state):
    """
    Given a city and state combination, returns the ZIP code(s).

    args:
    city -- a string denoting city name
    state -- a string denoting the state's abbreviation
    """
    if not comp_city or not comp_state:
        print('cannot leave either argument blank!')
        return
    url = 'http://api.zippopotam.us/us/' + comp_state + '/' + comp_city
    try:
        response = requests.get(url)
        response = response.json()
        places = response['places']
    except:
        print('invalid city/state combination!')
        return

    zip_codes = []
    for place in places:
        zip_codes.append(place['post code'])
    return zip_codes


def get_weather(city, state):
    """
    Gets the weather description of a zip code from the database if it exists.
    If it does not, accesses the noaa API to get the available weather data for the zip code,
    writes this information to the database, and writes it to the database for later use.

    args
    city -- a string denoting city name
    state -- a string denoting the state's abbreviation
    """
    print('================================================================================== BEGIN ==================================================================================')
    start = time.time()

    START_YEAR = '2012'
    END_YEAR = '2012'

    zip_codes = get_zip_codes(city, state)

    url = 'https://www.ncdc.noaa.gov/cdo-web/api/v2/data?datasetid=GSOM'
    try:
        for zip_code in zip_codes:
            url += '&locationid=ZIP:' + zip_code
    except:
        print('city, state pair produced no zip codes!')
        return
        
    url += '&startdate=' + START_YEAR + '-01-01&enddate=' + END_YEAR + '-12-31'
    url += '&datatypeid=PSUN' # Daily percent of possible sunshine for the period
    url += '&datatypeid=PRCP' # rainfall in in
    url += '&datatypeid=SNOW' # snowfall in in
    url += '&datatypeid=TAVG' # temperature average in fahrenheit
    url += '&datatypeid=AWND' # average wind speed in mph
    url += '&limit=1000'
    url += '&units=standard' # converts to standard
    url += '&includemetadata=false' # impove response time by preventing calc of result metadata    

    headers = {'token': 'YdgPMhahlBcRshMkgsmDaoFlvAFcjwnr'}

    response = requests.get(url, headers = headers)
    response = response.json()


    try:
        results = response['results']
    except:
        print('no noaa data found for zip codes')
        return

    # construct season_weather dictionary from response
    season_weather = {
        'spring': {'PRCP': None, 'SNOW': None, 'TAVG': None, 'PSUN': None, 'AWND': None},
        'summer': {'PRCP': None, 'SNOW': None, 'TAVG': None, 'PSUN': None, 'AWND': None},
        'autumn': {'PRCP': None, 'SNOW': None, 'TAVG': None, 'PSUN': None, 'AWND': None},
        'winter': {'PRCP': None, 'SNOW': None, 'TAVG': None, 'PSUN': None, 'AWND': None}
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
            if season_weather[season][datatype] is None:
                season_weather[season][datatype] = [value]
            else:
                season_weather[season][datatype].append(value)
        except:
            print('data error')
            return

    for season in season_weather:
        for attr in season_weather[season]:
            if season_weather[season][attr]:
                season_weather[season][attr] = sum(season_weather[season][attr]) / len(season_weather[season][attr])

    description = {'spring': '', 'summer': '', 'autumn': '', 'winter': ''}
    # build season attrs
    for season in season_weather:
        for attr in season_weather[season]:
            val = season_weather[season][attr]
            if val is not None:
                if attr == 'PRCP':
                    if val > 3:
                        description[season] += 'rainy, '
                    else:
                        description[season] += 'dry, '
                if attr == 'SNOW':
                    if val > 2:
                        description[season] += 'snowy, '
                    else:
                        description[season] += 'not snowy, '
                if attr == 'TAVG':
                    if val < 60:
                        description[season] += 'cold, '
                    elif val <= 80 and val > 60:
                        description[season] += 'cool, '
                    elif val < 100 and val > 80:
                        description[season] += 'warm, '
                    else:
                        description[season] += 'hot, '
                if attr == 'PSUN':
                    if val >= 80:
                        description[season] += 'sunny, '
                    elif val < 80 and val >= 50:
                        description[season] += 'cloudy, '
                    else:
                        description[season] += 'gray, '
                if attr == 'AWND':
                    if val >= 8:
                        description[season] += 'windy, '
                    else:
                        description[season] += 'calm, '

    print(season_weather)
    print(description)

    end = time.time()
    print(end - start)
    print('=================================================================================== END ===================================================================================')
    


    return

# call from command line using:
# python -c "from weather import get_weather; get_weather('CityName', 'ST_ABBR')"


