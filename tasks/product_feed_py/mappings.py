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

    colormaps = ColorMap.objects.values_list('external_color', 'allume_color')
    for colormap in colormaps:
        color_mapping[colormap[0]] = colormap[1]

    return color_mapping


def create_category_mapping():
    """
    Returns a dict of (primary_category, secondary_category) as keys mapped to 
    a tuple (allume_category_id, active). Allume_category_id is a long expected to be
    used in allume_category_mapping. Active is a boolean.
    """
    category_mapping = {}

    categorymaps = CategoryMap.objects.values_list('external_cat1', 'external_cat2', 'allume_category', 'active')
    for categorymap in categorymaps:
        key_tup = (categorymap[0], categorymap[1])
        val_tup = (categorymap[2], categorymap[3])
        category_mapping[key_tup] = val_tup

    return category_mapping


def create_allume_category_mapping():
    """
    Returns a dict of allume category names as keys mapped to a tuple of the allume
    category name and whether or not it is active. 1 is active and 0 is not active.
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

"""
class CategoryMap(models.Model):
    external_cat1 = models.CharField(max_length=250, blank=True, null=True)
    external_cat2 = models.CharField(max_length=250, blank=True, null=True)
    allume_category = models.ForeignKey(AllumeCategory, blank=True, null=True)
    active = models.BooleanField(default=False)
    pending_review = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
"""

