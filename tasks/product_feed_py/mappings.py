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

