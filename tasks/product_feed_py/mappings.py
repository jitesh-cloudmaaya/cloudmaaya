from django.db import connection

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
