# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import task, shared_task

from shopping_tool.models import AllumeClient360
from weather_service.models import Weather

from celery_once import QueueOnce

@task(base=QueueOnce)
def create_weather_data_from_allumeclient360():
    query_set = AllumeClient360.objects.filter(city__isnull=False, state__isnull=False).values('city', 'state').distinct()

    locations = []
    for pair in query_set:
        locations.append((pair['city'], pair['state']))

    # this creates or fetches the Weather objects
    Weather.objects.retrieve_weather_objects(locations)

    return
    