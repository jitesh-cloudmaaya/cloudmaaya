from __future__ import absolute_import, unicode_literals
from celery import task
from django.db import connection, transaction
import os
import time
from catalogue_service.settings import BASE_DIR
from celery_once import QueueOnce
from product_api.models import Product, AllumeCategory, CategoryMap, Merchant
from tasks.product_feed import ProductFeed
from tasks.product_feed_py.pepperjam import get_data, get_merchants
from datetime import datetime, timedelta
from elasticsearch_dsl import Search
from catalogue_service.settings import * # for the ES connection
from elasticsearch import Elasticsearch, helpers

@task(base=QueueOnce)
def pepper_jam_get_merchants():
    get_merchants()

@task(base=QueueOnce)
def pepperjam_pull():
    pf = ProductFeed(os.path.join(BASE_DIR, 'catalogue_service/pepperjam.yaml'))
    print("Creating temp directory for cleaned files")
    pf.make_temp_dir()
    print("Pulling and cleaning product data")
    pf.clean_data()
    print("Update API products table")
    pf.load_cleaned_data()
    print("Successfully updated API products table")

@task(base=QueueOnce)
def ran_delta_pull():
    pf = ProductFeed(os.path.join(BASE_DIR, 'catalogue_service/ran_delta.yaml'))
    print("Pulling delta files from FTP")
    pf.get_files_ftp()
    print("Decompressing files")
    pf.decompress_data()
    print("Cleaning files")
    pf.clean_data()
    print("Update API products table")
    pf.load_cleaned_data()
    print("Successfully updated API products table")

@task(base=QueueOnce)
def ran_full_pull():
    pf = ProductFeed(os.path.join(BASE_DIR, 'catalogue_service/ran.yaml'))
    print("Pulling full files from FTP")
    pf.get_files_ftp()
    print("Decompressing files")
    pf.decompress_data()
    print("Cleaning files")
    pf.clean_data()
    print("Update API products table")
    pf.load_cleaned_data()
    print("Successfully updated API products table")


@task(base=QueueOnce)
def build_client_360():
    cursor = connection.cursor()
    etl_file = open(os.path.join(BASE_DIR, 'tasks/client_360_sql/client_360.sql'))
    statement = etl_file.read()
    statements = statement.split(';')
    try:
        with transaction.atomic():
            for i in range(0, len(statements)):
                statement = statements[i]
                if statement.strip(): # avoid 'query was empty' operational error
                    cursor.execute(statement)
    finally:
        cursor.close()

@task(base=QueueOnce)
def update_client_360():
    cursor = connection.cursor()
    etl_file = open(os.path.join(BASE_DIR, 'tasks/client_360_sql/update_client_360.sql'))
    statement = etl_file.read()
    statements = statement.split(';')

    try:
        with transaction.atomic():
            for i in range(0, len(statements)):
                statement = statements[i]
                if statement.strip(): # avoid 'query was empty' operational error
                    cursor.execute(statement)
    finally:
        cursor.close()

@task(base=QueueOnce)
def build_lookmetrics():
    cursor = connection.cursor()
    etl_file = open(os.path.join(BASE_DIR, 'tasks/look_metrics_sql/look_metrics.sql'))
    statement = etl_file.read()
    statements = statement.split(';')
    try:
        with transaction.atomic():
            for i in range(0, len(statements)):
                statement = statements[i]
                if statement.strip(): # avoid 'query was empty' operational error
                    cursor.execute(statements[i])
    finally:
        cursor.close()


# attempt to write as raw SQL
# Model._meta._db_name #?

# -- attempt at writing the SQL to do the update
# -- we want to set inactive products to is_deleted = True
# -- change this to UPDATE product_api_product SET is_deleted = 1
# SELECT pap.product_id, pap.product_name, pap.merchant_id, pap.merchant_name FROM product_api_product pap
# LEFT JOIN product_api_categorymap pac ON pap.primary_category = pac.external_cat1
# AND pap.secondary_category = pac.external_cat2
# LEFT JOIN product_api_merchant pam ON pap.merchant_name = pam.name
# WHERE pac.active = 0 AND pam.active = 0;


# SELECT pap.product_id, pap.product_name, pap.merchant_id, pap.merchant_name FROM product_api_product pap
# LEFT JOIN product_api_categorymap pac ON pap.primary_category = pac.external_cat1
# AND pap.secondary_category = pac.external_cat2
# LEFT JOIN product_api_merchant pam ON pap.merchant_name = pam.name
# WHERE pac.active = 1 AND pam.active = 1 AND pac.pending_review = 0;

from django.db.models import Q
def test():
    start = time.time()
    # get the products of merchants that are inactive
    merchants = Merchant.objects.filter(active=False).values_list('name')
    # get the products of allume categories that are inactive
    allume_categories = AllumeCategory.objects.filter(active=False).values_list('name')
    # get the products of primary/secondary categories that are inactive
    categories_primary = CategoryMap.objects.filter(active=False).values_list('external_cat1')
    categories_secondary = CategoryMap.objects.filter(active=False).values_list('external_cat2')

    # prepare Q object
    q = Q(merchant_name__in = merchants) | Q (allume_category__in = allume_categories) | Q(primary_category__in = categories_primary, secondary_category__in = categories_secondary)

    # set up filters
    # merchant_products = Product.objects.filter(merchant_name__in = merchants)
    # allume_category_products = Product.objects.filter(allume_category__in = allume_categories)
    # category_products = Product.objects.filter(primary_category__in = categories_primary, secondary_category__in = categories_secondary)

    # union operator selects only distinct values by default
    # deleted_products = merchant_products.union(allume_category_products, category_products)

    deleted_products = Product.objects.filter(q) # distinct necessary?
    deleted_products.update(allume_score = 1)

    print 'just this part took %s seconds' % (time.time() - start)


@task(base=QueueOnce)
def index_deleted_products_cleanup(days_threshold = 5):
    """
    Creates a list of (product_id, merchant_id) tuples, which uniquely identify a record in the Product table.
    Then, creates a Search object for each tuple, executes the Search, and grabs the ES document id, if there
    was a hit. Lack of a hit signifies that the product was not in the index. Collects together all the ES 
    document ids and issues a bulk delete command on them.

    Args:
        days_threshold (int): An optional parameter that filters the Products to perform an ES query on. Serves
        as the threshold of how far back the updated_at parameter will be checked against. Defaults to 5 days.
    """
    start = time.time()
    # get the products of merchants that are inactive
    merchants = Merchant.objects.filter(active=False).values_list('name')
    # get the products of allume categories that are inactive
    allume_categories = AllumeCategory.objects.filter(active=False).values_list('name')
    # get the products of primary/secondary categories that are inactive
    categories = CategoryMap.objects.filter(active=False)
    categories_primary = categories.values_list('external_cat1')
    categories_secondary = categories.values_list('external_cat2')

    # prepare Q object
    q = Q(merchant_name__in = merchants) | Q (allume_category__in = allume_categories) | Q(primary_category__in = categories_primary, secondary_category__in = categories_secondary)

    deleted_products = Product.objects.filter(q).distinct() # distinct necessary?
    deleted_products.update(is_deleted = 1)

    print 'just this part took %s seconds' % (time.time() - start)

    datetime_threshold = datetime.now() - timedelta(days = days_threshold) # query products as far back as days_threshold
    deleted_products = Product.objects.filter(updated_at__gte = datetime_threshold, is_deleted = True)
    deleted_products = deleted_products.values_list('product_id', 'merchant_id') # ids are longs

    document_ids = []
    # issue search to find document ids of these products
    for deleted_product in deleted_products:
        product_id = str(deleted_product[0])
        merchant_id = str(deleted_product[1])
        # delete by query from index
        deleted_product = Search(index="products").query("match", product_id = product_id) \
            .query("match", merchant_id = merchant_id)
        response = deleted_product.execute()
        response = response.to_dict()

        hits = response['hits']['hits']
        if len(hits): # a document for product was found
            document_id = hits[0]['_id'] # a match query on a unique index pair should only match one product
            document_ids.append(document_id)
        # otherwise document for product already does not exist in index

    # construct actions for bulk
    actions = []

    for document_id in document_ids:
        action = {
          '_op_type': 'delete',
          '_index': 'products',
          '_type': 'product',
          '_id': document_id
        }
        actions.append(action)

    # using these document_ids, issue a bulk delete on them
    helpers.bulk(CLIENT, actions)

    print 'process took %s seconds' % (time.time() - start)
