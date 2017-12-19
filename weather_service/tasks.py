# Create your tasks here
from __future__ import absolute_import, unicode_literals

import re
import json

from celery import task, shared_task
from celery_once import QueueOnce

from shopping_tool.models import AllumeClient360
from weather_service.models import Weather


@task(base=QueueOnce)
def create_weather_data_from_allumeclient360():
    query_set = AllumeClient360.objects.filter(where_live__isnull=False).values('where_live').distinct()

    locations = []
    for value in query_set:
        extracted = value['where_live']
        regex = '^([^}]+)'
        obj = re.search(regex, extracted).group(0)
        obj += '}'

        obj = json.loads(obj)

        if len(obj) == 2:
            if type(obj['state']) != int: # non us locations have a 0 for state
                locations.append((obj['city'], obj['state']))

    # this creates or fetches the Weather objects
    Weather.objects.retrieve_weather_objects(locations) # comment out when ready again

    return
        