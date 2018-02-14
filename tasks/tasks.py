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
# comment and redeploy
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
