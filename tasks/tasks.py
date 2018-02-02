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

@task(base=QueueOnce)
def delete_products_from_index():
    # poll products_api_product for products where is_deleted = true
    deleted_product_ids = Product.objects.filter(is_deleted = True).values_list('id')
    # issue command on es index to delete those ids

