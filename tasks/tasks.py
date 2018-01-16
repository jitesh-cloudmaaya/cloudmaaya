from __future__ import absolute_import, unicode_literals
from celery import task
from django.db import connection, transaction
import os
from catalogue_service.settings import BASE_DIR
from celery_once import QueueOnce
from tasks.product_feed import ProductFeed


@task(base=QueueOnce)
def ran_delta_pull():
    pf = ProductFeed(os.path.join(BASE_DIR, 'catalogue_service/ran_delta.yaml'))
    print("Pulling Files from FTP")
    pf.get_files_ftp()
    print("Loading Data to DB and Updating Products")
    pf.process_data()
    print("Updating the API Products Table")
    pf.update_products_api()

@task(base=QueueOnce)
def ran_full_pull():
    pf = ProductFeed(os.path.join(BASE_DIR, 'catalogue_service/ran.yaml'))
    print("Pulling Files from FTP")
    pf.get_files_ftp()
    print("Loading Data to DB and Updating Products")
    pf.process_data()
    print("Updating the API Products Table")
    pf.update_products_api()

@task(base=QueueOnce)
def build_client_360():
	cursor = connection.cursor()
	etl_file = open(os.path.join(BASE_DIR, 'tasks/client_360_sql/client_360.sql'))
	statement = etl_file.read()
	cursor.execute(statement)

@task(base=QueueOnce)
def update_client_360():
    cursor = connection.cursor()
    etl_file = open(os.path.join(BASE_DIR, 'tasks/client_360_sql/update_client_360.sql'))
    statement = etl_file.read()
    cursor.execute(statement)

# new tasks
@task(base=QueueOnce)
def ran_delta_pull_new():
    pf = ProductFeed(os.path.join(BASE_DIR, 'catalogue_service/ran_delta.yaml'))
    print("Pulling delta files from FTP")
    pf.get_files_ftp()
    print("Decompressing files")
    pf.decompress_data()
    print("Cleaning files")
    pf.clean_data()
    print("Load data to API products table")
    pf.load_cleaned_data()

@task(base=QueueOnce)
def ran_full_pull_new():
    pf = ProductFeed(os.path.join(BASE_DIR, 'catalogue_service/ran.yaml'))
    print("Pulling full files from FTP")
    pf.get_files_ftp()
    print("Decompressing files")
    pf.decompress_data()
    print("Cleaning files")
    pf.clean_data()
    print("Load data to API products table")
    pf.load_cleaned_data()
