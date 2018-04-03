import os
import yaml
from django.db import connection
from product_api.models import Merchant, Network, CategoryMap, ColorMap, AllumeCategory, SizeMap, ShoeSizeMap, SizeTermMap
from catalogue_service.settings import BASE_DIR

def create_merchant_mapping():
    """
    Returns a dict of merchant_ids as longs mapped to whether or not that
    merchant is active as a boolean.
    """
    merchant_mapping = {}

    merchants = Merchant.objects.values_list('external_merchant_id', 'active')
    for merchant in merchants:
        merchant_mapping[merchant[0]] = merchant[1]

    return merchant_mapping

def create_color_mapping():
    """
    Returns a dict of external_color mapped to the allume_color. Both values are strings.
    Both variables are lower case strings.
    """

    color_mapping = {}

    color_maps = ColorMap.objects.values_list('external_color', 'allume_color')
    for color_map in color_maps:
        color_mapping[color_map[0]] = color_map[1]

    return color_mapping


def create_category_mapping():
    """
    Returns a dict of (primary_category, secondary_category) as keys mapped to 
    a tuple (allume_category_id, active). Allume_category_id is a long expected to be
    used in allume_category_mapping. Active is a boolean.
    """
    category_mapping = {}

    category_maps = CategoryMap.objects.values_list('external_cat1', 'external_cat2', 'allume_category', 'turned_on', 'id', 'merchant_name')
    for category_map in category_maps:
        key_tup = (category_map[0], category_map[1])
        val_tup = (category_map[2], category_map[3], category_map[4], category_map[5])
        category_mapping[key_tup] = val_tup

    return category_mapping


def create_allume_category_mapping():
    """
    Returns a dict of allume category names as keys mapped to a tuple of the allume
    category name and whether or not it is active. Active is a boolean.
    """
    allume_category_mapping = {}

    allume_categories = AllumeCategory.objects.values_list('id', 'name', 'active')

    for allume_category in allume_categories:
        val_tup = (allume_category[1], allume_category[2])
        allume_category_mapping[allume_category[0]] = val_tup

    return allume_category_mapping


def create_size_mapping():
    """
    Returns a dict of merchant_size mapped to the allume_size. Both values are strings.
    """
    filepath = os.path.join(BASE_DIR, 'product_api/fixtures/SizeMap.yaml')
    f = open(filepath, 'r')
    size_maps = yaml.load(f)
    size_mapping = {}
    for size_map in size_maps:
        fields = size_map['fields']
        sm = SizeMap(merchant_size = fields['merchant_size'].decode('UTF-8'), allume_size = fields['allume_size'].decode('UTF-8'))
        size_mapping[sm.merchant_size] = sm.allume_size

    return size_mapping

def create_shoe_size_mapping():
    """
    Returns a dict of merchant_size mapped to the allume_size for shoes. Both values are strings.
    """
    filepath = os.path.join(BASE_DIR, 'product_api/fixtures/ShoeSizeMap.yaml')
    f = open(filepath, 'r')
    shoe_size_maps = yaml.load(f)
    shoe_size_mapping = {}
    for shoe_size_map in shoe_size_maps:
        fields = shoe_size_map['fields']
        ssm = ShoeSizeMap(merchant_size = fields['merchant_size'].decode('UTF-8'), allume_size = fields['allume_size'].decode('UTF-8'))
        shoe_size_mapping[ssm.merchant_size] = ssm.allume_size

    return shoe_size_mapping

def create_size_term_mapping():
    """
    Returns a dict of merchant_phrase mapped to the allume_attribute for term expansion.
    Both values are strings.
    """
    filepath = os.path.join(BASE_DIR, 'product_api/fixtures/SizeTermMap.yaml')
    f = open(filepath, 'r')
    size_term_maps = yaml.load(f)
    size_term_mapping = {}
    for size_term_map in size_term_maps:
        fields = size_term_map['fields']
        stm = SizeTermMap(merchant_phrase = fields['merchant_phrase'].decode('UTF-8'), allume_attribute = fields['allume_attribute'].decode('UTF-8'))
        size_term_mapping[stm.merchant_phrase] = stm.allume_attribute

    return size_term_mapping

def add_new_merchant(external_merchant_id, name, network, active = False):
    Merchant.objects.create(external_merchant_id = external_merchant_id, name = name, network = network, active = active)

def get_network(network_name):
    try:
        return Network.objects.get(name = network_name)
    except Network.DoesNotExist:
        Network.objects.create(name = network_name, active = True)
        return Network.objects.get(name = network_name)

def is_merchant_in_category(category_mapping, identifier, merchant_name):
    allume_category_id, categories_are_active, category_map_id, merchant_name_list = category_mapping[identifier]

    if merchant_name_list:
        merchants_list = merchant_name_list.split("|")
    else:
        merchants_list = []

    if merchant_name not in merchants_list:

        merchants_list.append(merchant_name)

        cm = CategoryMap.objects.get(id = category_map_id)
        #print merchants_list
        merchants_list.sort()
        cm.merchant_name = '|'.join(set(merchants_list))
        cm.save()

    return True


def add_category_map(external_cat1, external_cat2, merchant_name, allume_category, active = False, pending_review=True):
    CategoryMap.objects.create(external_cat1 = external_cat1, external_cat2 = external_cat2, merchant_name = merchant_name,
                               allume_category = None, turned_on = active, pending_review=pending_review)
    return True


def is_merchant_active(merchant_id, merchant_name, network, merchant_mapping):
    """
    Takes in as arguments a str merchant_id, a string merchant_name, a network
    id corresponding to the appropriate Network object, a dictionary, merchant_mapping,
    created with each call to the clean_data function. Creates the merchant if it does
    not exist. Returns True if the merchant is in the merchant_mapping and active,
    False otherwise.
    """
    try:
        merchant_id = long(merchant_id)
        # if not in the map
        if merchant_id not in merchant_mapping.keys():
            # create a new instance and save
            add_new_merchant(merchant_id, merchant_name, network, False)
            # edit the passed-in dict
            merchant_mapping[merchant_id] = False
        if merchant_mapping[merchant_id]:
            return True
        return False
    except KeyError:
        return False

def are_categories_active(primary_category, secondary_category, category_mapping, allume_category_mapping, input_merchant_name):
    """
    Takes in a primary category and a secondary category as strings and a
    category_mapping dictionary and checks to see if they constitute an
    undiscovered pair, adding it to the relevant table if so. Additionally,
    checks to see if they are active at the primary and secondary category level
    as well as the allume category level. Returns the allume category if so and
    False otherwise.
    """
    # print category_mapping
    try:
        identifier = (primary_category, secondary_category)
        if identifier not in category_mapping.keys():
            add_category_map(primary_category, secondary_category, input_merchant_name, None, False, True)
            # edit the mapping instance
            category_mapping[identifier] = (None, False, -1, input_merchant_name)
            # print discovered categories pair
            #print identifier

        allume_category_id, categories_are_active, category_map_id, merchant_name = category_mapping[identifier]
        # if id == -1, then category is newly added with merchant_name, no need to backfill
        if category_map_id != -1:
            # check if the merchant_name for this category exists, if not add it
            is_merchant_in_category(category_mapping, identifier, input_merchant_name)

        if allume_category_id == None:
            # allume_category_id is None because it is either a newly discovered category
            # or a category that is still pending review post-discovery
            return False
        # check if the primary and secondary categories are active
        if not categories_are_active:
            return False
        allume_category, allume_category_is_active = allume_category_mapping[allume_category_id]
        # check allume_category is active
        if not allume_category_is_active:
            return False
        return allume_category

    except KeyError:
        return False
