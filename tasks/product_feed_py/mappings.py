from django.db import connection
from product_api.models import Merchant, Network, CategoryMap, ColorMap, AllumeCategory

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

    category_maps = CategoryMap.objects.values_list('external_cat1', 'external_cat2', 'allume_category', 'active')
    for category_map in category_maps:
        key_tup = (category_map[0], category_map[1])
        val_tup = (category_map[2], category_map[3])
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

def add_new_merchant(external_merchant_id, name, network, active = False):
    Merchant.objects.create(external_merchant_id = external_merchant_id, name = name, network = network, active = active)

def get_network(network_name):
    return Network.objects.get(name = network_name)

def add_category_map(external_cat1, external_cat2, allume_category, active = False, pending_review=True):
    CategoryMap.objects.create(external_cat1 = external_cat1, external_cat2 = external_cat2, 
                               allume_category = None, active = active, pending_review=pending_review)

def is_merchant_active(merchant_id, merchant_name, network, merchant_mapping):
    """
    Takes in as arguments a str merchant_id, a string merchant_name, a network
    id corresponding to the appropriate Network object, a dictionary, merchant_mapping,
    created with each call to the clean_data function. Creates the merchant if it does
    not exist. Returns True if the merchant is in the merchant_mapping and active,
    False otherwise.
    """
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

def are_categories_active(primary_category, secondary_category, category_mapping, allume_category_mapping):
    """
    Takes in a primary category and a secondary category as strings and a
    category_mapping dictionary and checks to see if they constitute an
    undiscovered pair, adding it to the relevant table if so. Additionally,
    checks to see if they are active at the primary and secondary category level
    as well as the allume category level. Returns the allume category if so and
    False otherwise.
    """
    identifier = (primary_category, secondary_category)
    if identifier not in category_mapping.keys():
        mappings.add_category_map(primary_category, secondary_category, None, False, True)
        # edit the mapping instance
        category_mapping[identifier] = (None, False)
        # print discovered categories pair
        print identifier
    allume_category_id, categories_are_active = category_mapping[identifier]
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
