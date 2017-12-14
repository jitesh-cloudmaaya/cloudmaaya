# # setup exploratory environment
# from catalogue_service import settings
# from django.core.management import setup_environ
# setup_environ(settings)


from shopping_tool.models import AllumeClient360
from weather_service.models import Weather

print('Begin attempt')
# query_set = AllumeClient360.objects.filter(city__isnull=False, state__isnull=False) # .distinct
query_set = AllumeClient360.objects.filter(city__isnull=False, state__isnull=False).values('city', 'state').distinct() # speed of this configuration?
# print(query_set.count())

locations = []
for pair in query_set:
    locations.append((pair['city'], pair['state']))

print(locations)
    # print('city, state pair is: (' + pair['city'] + ', ' + pair['state'] + ')')
# for model in query_set:
#     city = model.city
#     state = model.state

#     print('city, state pair is: (' + city + ', ' + state + ')')


# in theory, we can call bulk_weather retrieval here

# this creates or fetches the objects...
# Weather.objects.retrieve_weather_objects(locations)

# need to define behavior cases of weather_retrieval more clearly





print('end attempt')