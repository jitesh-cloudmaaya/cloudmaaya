# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task

from shopping_tool.models import AllumeClient360
from weather_service.models import Weather


@shared_task
def add(x, y):
    return x + y

# begin celery task for weather_data

@shared_task
def create_weather_data_from_allumeclient360():
    print('Begin attempt')

    query_set = AllumeClient360.objects.filter(city__isnull=False, state__isnull=False).values('city', 'state').distinct() # speed of this configuration?
    print(query_set.count())    


    locations = []
    for pair in query_set:
        locations.append((pair['city'], pair['state']))

    print(locations)

    # in theory, we can call bulk_weather retrieval here

    # this creates or fetches the objects...
    # Weather.objects.retrieve_weather_objects(locations)

    # need to define behavior cases of weather_retrieval more clearly

    print('End attempt')


    return