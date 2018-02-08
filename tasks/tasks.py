from __future__ import absolute_import, unicode_literals
from celery import task
from django.db import connection, transaction
import os
from catalogue_service.settings import BASE_DIR
from celery_once import QueueOnce
from product_api.models import Product
from tasks.product_feed import ProductFeed
from tasks.product_feed_py.pepperjam import get_data, get_merchants

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


from elasticsearch_dsl import Search
from catalogue_service.settings import * # for the ES connection
###### A COUPLE TRIES AT index cleanup
@task(base=QueueOnce)
def index_cleanup1():
    """
    Defines one Search that matches where is_deleted = True and then issues a delete command.
    Handled using only elasticsearch_dsl.
    """
    print('Finding all deleted products')
    deleted_products = Search().query("match", is_deleted = True)
    print('Removing deleted products from the search index')
    deleted_products.delete()
    # response = deleted_products.execute()
    # print response.to_dict()

@task(base=QueueOnce)
def index_cleanup2():
    """
    Creates a list of (product_id, merchant_id) tuples, which uniquely identify a record in the Product table.
    Then, creates a Search object for each tuple and issues the delete command for each one. Uses both Django's
    ORM and elasticsearch_dsl and seems less efficient than method 1.
    """
    # poll products_api_product for products where is_deleted = true
    deleted_products = Product.objects.filter(is_deleted = True).values_list('product_id', 'merchant_id') # ids are longs
    # issue command on es index to delete those ids
    i = 0
    for deleted_product in deleted_products:
        product_id = str(deleted_product[0])
        merchant_id = str(deleted_product[1])
        # delete by query from index
        deleted_product = Search().query("match", product_id = product_id, merchant_id = merchant_id)
        deleted_product.delete()

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

