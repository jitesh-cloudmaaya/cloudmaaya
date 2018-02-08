from __future__ import absolute_import, unicode_literals
from celery import task
from django.db import connection, transaction
import os
from catalogue_service.settings import BASE_DIR
from celery_once import QueueOnce
from product_api.models import Product
from tasks.product_feed import ProductFeed
from tasks.product_feed_py.pepperjam import get_data, get_merchants
from datetime import datetime, timedelta
from elasticsearch_dsl import Search
from catalogue_service.settings import * # for the ES connection

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


###### A COUPLE TRIES AT index cleanup
# @task(base=QueueOnce)
# def index_cleanup1():
#     """
#     Defines one Search that matches where is_deleted = True and then issues a delete command.
#     Handled using only elasticsearch_dsl.
#     """
#     print('Finding all deleted products')
#     deleted_products = Search(index="products").query("match", is_deleted = True)
#     print('Removing deleted products from the search index')
#     deleted_products.delete()
#     # response = deleted_products.execute()
#     # print response.to_dict()


# def set_deleted_pepperjam_products(threshold = 12):
#     """
#     Helper method for use in the main get_data method. Collects a list of Pepperjam products
#     that should have been upserted in the current run. For those that were not upserted, determined
#     by a settable time threshold, set those products to a status of is_deleted = True.
#     Args:
#         threshold (int): The time threshold in hours. If the updated_at value of a record is threshold
#         or more hours old, conclude it was not updated in the current upsert and set to deleted.
#     """
#     # id of the pepperjam network for use in merchants' network_id
#     pepperjam_id = Network.objects.get(name='PepperJam').id
#     # get the pepperjam merchants that were active (and hence were just updated)
#     merchants = Merchant.objects.filter(active=True, network_id = pepperjam_id) # multiple arguments over chaining for performance
#     merchant_ids = merchants.values_list('external_merchant_id')
#     # get the products of these merchants
#     products = Product.objects.filter(merchant_id__in = merchant_ids) # up to here is confirmed what we want
#     datetime_threshold = datetime.now() - timedelta(hours = threshold) # comparison threshold is 12 hours ago or more
#     deleted_products = products.filter(updated_at__lte = datetime_threshold)
#     # set is deleted for all of them and save in bulk (WILL NOT perform Product save callbacks)
#     deleted_products.update(is_deleted = True)



@task(base=QueueOnce)
def index_deleted_products_cleanup(days_threshold = 5):
    """
    Creates a list of (product_id, merchant_id) tuples, which uniquely identify a record in the Product table.
    Then, creates a Search object for each tuple and issues the delete command for each one. Uses both Django's
    ORM and elasticsearch_dsl and seems less efficient than method 1.

    Args:
        days_threshold (int): An optional parameter that filters the Products to perform an ES query on. Serves
        as the threshold of how far back the updated_at parameter will be checked against. Defaults to 5 days.
    """
    # poll products_api_product for products where is_deleted = true
    datetime_threshold = datetime.now() -  timedelta(days = days_threshold) # query products as far as days_threshold back
    deleted_products = Product.objects.filter(updated_at__gte = datetime_threshold, is_deleted = True)
    deleted_products = deleted_products.values_list('product_id', 'merchant_id') # ids are longs
    # issue command on es index to delete those ids
    for deleted_product in deleted_products:
        product_id = str(deleted_product[0])
        merchant_id = str(deleted_product[1])
        # delete by query from index
        deleted_product = Search(index="products").query("match", product_id = product_id) \
            .query("match", merchant_id = merchant_id)
        deleted_product.delete()

    # s = Search(index="products") \
    #     .query("match_phrase", product_name=text_query)[0:10]

    # faster ways that don't involve calling ES for every product_id?
    # delete on is_deleted = True matches in product index?
    # s = Search().query("match", is_deleted = True)
    # s.delete()

    # thoughts
    # talking to ES API...?
    # https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-delete.html
    # for product_id in deleted_product_ids:
    # REST_API = 'DELETE products/' + str(product_id)
    # issue(REST_API)

    # using elasticsearch (aka elasticsearch-py client and not dsl, we have both)
    # use the delete(*args, **kwargs) method

