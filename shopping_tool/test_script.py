# # setup exploratory environment
# from catalogue_service import settings
# from django.core.management import setup_environ
# setup_environ(settings)


from shopping_tool.models import AllumeClient360

print('Begin attempt')
# query_set = AllumeClient360.objects.filter(city__isnull=False, state__isnull=False) # .distinct
query_set = AllumeClient360.objects.filter(city__isnull=False, state__isnull=False).values('city', 'state').distinct() # speed of this configuration?
print(query_set.count())

print(query_set)

for pair in query_set:
    print('city, state pair is: (' + pair['city'] + ', ' + pair['state'] + ')')
# for model in query_set:
#     city = model.city
#     state = model.state

#     print('city, state pair is: (' + city + ', ' + state + ')')




print('end attempt')