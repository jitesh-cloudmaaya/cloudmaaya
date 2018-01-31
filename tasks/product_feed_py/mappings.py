from django.db import connection
from product_api.models import Merchant, Network, CategoryMap

def create_merchant_mapping():
    cursor = connection.cursor()
    cursor.execute("SELECT external_merchant_id, active FROM product_api_merchant")

    merchant_mapping = {}
    for tup in cursor.fetchall():
        merchant_mapping[tup[0]] = tup[1]

    return merchant_mapping


def create_color_mapping():
    cursor = connection.cursor()
    cursor.execute("SELECT external_color, allume_color FROM product_api_colormap")

    color_mapping = {}
    for tup in cursor.fetchall():
        color_mapping[tup[0]] = tup[1]

    return color_mapping


def create_category_mapping():
    cursor = connection.cursor()
    cursor.execute("SELECT external_cat1, external_cat2, allume_category_id, active FROM product_api_categorymap")

    category_mapping = {}
    for tup in cursor.fetchall():
        category_pair = (tup[0], tup[1])
        info = (tup[2], tup[3])
        category_mapping[category_pair] = info

    return category_mapping


def create_allume_category_mapping():
    """
    Will return a dict of allume category names as keys mapped to whether or not that
    allume category is active, 1 is active and 0 is not active.
    """

    cursor = connection.cursor()
    cursor.execute("SELECT id, name, active FROM product_api_allumecategory")

    allume_category_mapping = {}
    for tup in cursor.fetchall():
        info = (tup[1], tup[2])
        allume_category_mapping[tup[0]] = info

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
    except:
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
    try:
        identifier = (primary_category, secondary_category)
        if identifier not in category_mapping.keys():
            add_category_map(primary_category, secondary_category, None, False, True)
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
    except:
        return False

