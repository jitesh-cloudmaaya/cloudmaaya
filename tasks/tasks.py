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

def test_for_es(days_threshold = 5):
    datetime_threshold = datetime.now() -  timedelta(days = days_threshold) # query products as far as days_threshold back
    deleted_products = Product.objects.filter(updated_at__gte = datetime_threshold, is_deleted = True)
    deleted_products = deleted_products.values_list('product_id', 'merchant_id') # ids are longs
    # issue command on es index to delete those ids
    print len(deleted_products)

    deleted_products = Product.objects.filter(is_deleted = True)
    deleted_products = deleted_products.values_list('product_id', 'merchant_id')
    print len(deleted_products)

    return

    for deleted_product in deleted_products:
        product_id = str(deleted_product[0])
        merchant_id = str(deleted_product[1])
        # delete by query from index
        deleted_product = Search(index="products").query("match", product_id = product_id) \
            .query("match", merchant_id = merchant_id)
        response = deleted_product.execute()
        print response.to_dict()

# if we want to use bulk
# my understanding is that we would have to get a the collection of documents
# and then issue a delete on those
from elasticsearch import Elasticsearch, helpers
from catalogue_service.settings import client # es connection moved to elasticsearch-py as client var

# the following example inserts the JSON document to the "products" index, under a type called "_doc"
# with an id of 1
# PUT twitter/_doc/1
# {
#     "user" : "kimchy",
#     "post_date" : "2009-11-15T14:12:12",
#     "message" : "trying out Elasticsearch"
# }

# elasticseach.helpers.bulk example
# actions = [
#   {
#     "_index": "tickets-index",
#     "_type": "tickets",
#     "_id": j,
#     "_source": {
#         "any":"data" + str(j),
#         "timestamp": datetime.now()}
#   }
#   for j in range(0, 10)
# ]

# helpers.bulk(es, actions)

# attempt at using bulk to bulk add documents
# op type defaults to index
def attempt_add_bulk():
    actions = [
      {
        "_op_type": "index",
        "_index": "products",
        "_type": "product",
        "_id": 33000000,
        "_source": {
          "long_product_description": "this the the longer",
          "end_date": None,
          "product_url": "http://example.com",
          "color": "blue",
          "gender": "MEN",
          "keywords": "",
          "begin_date": None,
          "discount": 0,
          "created_at": None,
          "merchant_id": 13816,
          "product_image_url": "lol",
          "availability": "in-stock",
          "retail_price": 388,
          "is_trending": False,
          "is_deleted": False,
          "updated_at": "2018-01-30T04:42:37.000Z",
          "primary_category": "Apparel & Accessories",
          "product_id": 1000001,
          "short_product_description": "shorter",
          "@version": "1",
          "currency": "USD",
          "id": 230000000,
          "sku": "13058br9nch9mp",
          "brand": "Reformation",
          "is_best_seller": False,
          "shipping_price": 0,
          "merchant_color": "August",
          "raw_product_url": "derived",
          "buy_url": "",
          "merchant_name": "Reformation",
          "allume_size": None,
          "manufacturer_name": "Reformation",
          "discount_type": "amount",
          "product_name": "Thistle Dress Mk35",
          "sale_price": 0,
          "secondary_category": "Clothing~~Dresses",
          "product_type": "",
          "@timestamp": "2018-02-08T04:18:02.210Z",
          "size": "4P",
          "material": "",
          "manufacturer_part_number": "1301882CHR",
          "style": "",
          "current_price": 388,
          "allume_category": "Dresses",
          "allume_score": 0,
          "age": "ADULT"
        }
      },
      {
        "_op_type": "index",
        "_index": "products",
        "_type": "product",
        "_id": 33000001,
        "_source": {
          "long_product_description": "this the the longer",
          "end_date": None,
          "product_url": "http://example.com",
          "color": "blue",
          "gender": "MEN",
          "keywords": "",
          "begin_date": None,
          "discount": 0,
          "created_at": None,
          "merchant_id": 13816,
          "product_image_url": "lol",
          "availability": "in-stock",
          "retail_price": 388,
          "is_trending": False,
          "is_deleted": False,
          "updated_at": "2018-01-30T04:42:37.000Z",
          "primary_category": "Apparel & Accessories",
          "product_id": 1000002,
          "short_product_description": "shorter",
          "@version": "1",
          "currency": "USD",
          "id": 230000000,
          "sku": "13058br9nch9mp",
          "brand": "Reformation",
          "is_best_seller": False,
          "shipping_price": 0,
          "merchant_color": "August",
          "raw_product_url": "derived",
          "buy_url": "",
          "merchant_name": "Reformation",
          "allume_size": None,
          "manufacturer_name": "Reformation",
          "discount_type": "amount",
          "product_name": "Thistle Dress Mk45",
          "sale_price": 0,
          "secondary_category": "Clothing~~Dresses",
          "product_type": "",
          "@timestamp": "2018-02-08T04:18:02.210Z",
          "size": "4P",
          "material": "",
          "manufacturer_part_number": "1301882CHR",
          "style": "",
          "current_price": 388,
          "allume_category": "Dresses",
          "allume_score": 0,
          "age": "ADULT"
        }
      },
      {
        "_op_type": "index",
        "_index": "products",
        "_type": "product",
        "_id": 33000002,
        "_source": {
          "long_product_description": "this the the longer",
          "end_date": None,
          "product_url": "http://example.com",
          "color": "blue",
          "gender": "MEN",
          "keywords": "",
          "begin_date": None,
          "discount": 0,
          "created_at": None,
          "merchant_id": 13816,
          "product_image_url": "lol",
          "availability": "in-stock",
          "retail_price": 388,
          "is_trending": False,
          "is_deleted": False,
          "updated_at": "2018-01-30T04:42:37.000Z",
          "primary_category": "Apparel & Accessories",
          "product_id": 1000003,
          "short_product_description": "shorter",
          "@version": "1",
          "currency": "USD",
          "id": 230000000,
          "sku": "13058br9nch9mp",
          "brand": "Reformation",
          "is_best_seller": False,
          "shipping_price": 0,
          "merchant_color": "August",
          "raw_product_url": "derived",
          "buy_url": "",
          "merchant_name": "Reformation",
          "allume_size": None,
          "manufacturer_name": "Reformation",
          "discount_type": "amount",
          "product_name": "Thistle Dress Mk45",
          "sale_price": 0,
          "secondary_category": "Clothing~~Dresses",
          "product_type": "",
          "@timestamp": "2018-02-08T04:18:02.210Z",
          "size": "4P",
          "material": "",
          "manufacturer_part_number": "1301882CHR",
          "style": "",
          "current_price": 388,
          "allume_category": "Dresses",
          "allume_score": 0,
          "age": "ADULT"
        }
      },
      {
        "_op_type": "index",
        "_index": "products",
        "_type": "product",
        "_id": 33000003,
        "_source": {
          "long_product_description": "this the the longer",
          "end_date": None,
          "product_url": "http://example.com",
          "color": "blue",
          "gender": "MEN",
          "keywords": "",
          "begin_date": None,
          "discount": 0,
          "created_at": None,
          "merchant_id": 13816,
          "product_image_url": "lol",
          "availability": "in-stock",
          "retail_price": 388,
          "is_trending": False,
          "is_deleted": False,
          "updated_at": "2018-01-30T04:42:37.000Z",
          "primary_category": "Apparel & Accessories",
          "product_id": 1000004,
          "short_product_description": "shorter",
          "@version": "1",
          "currency": "USD",
          "id": 230000000,
          "sku": "13058br9nch9mp",
          "brand": "Reformation",
          "is_best_seller": False,
          "shipping_price": 0,
          "merchant_color": "August",
          "raw_product_url": "derived",
          "buy_url": "",
          "merchant_name": "Reformation",
          "allume_size": None,
          "manufacturer_name": "Reformation",
          "discount_type": "amount",
          "product_name": "Thistle Dress Mk45",
          "sale_price": 0,
          "secondary_category": "Clothing~~Dresses",
          "product_type": "",
          "@timestamp": "2018-02-08T04:18:02.210Z",
          "size": "4P",
          "material": "",
          "manufacturer_part_number": "1301882CHR",
          "style": "",
          "current_price": 388,
          "allume_category": "Dresses",
          "allume_score": 0,
          "age": "ADULT"
        }
      },
      {
        "_op_type": "index",
        "_index": "products",
        "_type": "product",
        "_id": 33000004,
        "_source": {
          "long_product_description": "this the the longer",
          "end_date": None,
          "product_url": "http://example.com",
          "color": "blue",
          "gender": "MEN",
          "keywords": "",
          "begin_date": None,
          "discount": 0,
          "created_at": None,
          "merchant_id": 13816,
          "product_image_url": "lol",
          "availability": "in-stock",
          "retail_price": 388,
          "is_trending": False,
          "is_deleted": False,
          "updated_at": "2018-01-30T04:42:37.000Z",
          "primary_category": "Apparel & Accessories",
          "product_id": 1000005,
          "short_product_description": "shorter",
          "@version": "1",
          "currency": "USD",
          "id": 230000000,
          "sku": "13058br9nch9mp",
          "brand": "Reformation",
          "is_best_seller": False,
          "shipping_price": 0,
          "merchant_color": "August",
          "raw_product_url": "derived",
          "buy_url": "",
          "merchant_name": "Reformation",
          "allume_size": None,
          "manufacturer_name": "Reformation",
          "discount_type": "amount",
          "product_name": "Thistle Dress Mk45",
          "sale_price": 0,
          "secondary_category": "Clothing~~Dresses",
          "product_type": "",
          "@timestamp": "2018-02-08T04:18:02.210Z",
          "size": "4P",
          "material": "",
          "manufacturer_part_number": "1301882CHR",
          "style": "",
          "current_price": 388,
          "allume_category": "Dresses",
          "allume_score": 0,
          "age": "ADULT"
        }
      },
      {
        "_op_type": "index",
        "_index": "products",
        "_type": "product",
        "_id": 33000005,
        "_source": {
          "long_product_description": "this the the longer",
          "end_date": None,
          "product_url": "http://example.com",
          "color": "blue",
          "gender": "MEN",
          "keywords": "",
          "begin_date": None,
          "discount": 0,
          "created_at": None,
          "merchant_id": 13816,
          "product_image_url": "lol",
          "availability": "in-stock",
          "retail_price": 388,
          "is_trending": False,
          "is_deleted": False,
          "updated_at": "2018-01-30T04:42:37.000Z",
          "primary_category": "Apparel & Accessories",
          "product_id": 1000006,
          "short_product_description": "shorter",
          "@version": "1",
          "currency": "USD",
          "id": 230000000,
          "sku": "13058br9nch9mp",
          "brand": "Reformation",
          "is_best_seller": False,
          "shipping_price": 0,
          "merchant_color": "August",
          "raw_product_url": "derived",
          "buy_url": "",
          "merchant_name": "Reformation",
          "allume_size": None,
          "manufacturer_name": "Reformation",
          "discount_type": "amount",
          "product_name": "Thistle Dress Mk45",
          "sale_price": 0,
          "secondary_category": "Clothing~~Dresses",
          "product_type": "",
          "@timestamp": "2018-02-08T04:18:02.210Z",
          "size": "4P",
          "material": "",
          "manufacturer_part_number": "1301882CHR",
          "style": "",
          "current_price": 388,
          "allume_category": "Dresses",
          "allume_score": 0,
          "age": "ADULT"
        }
      },
      {
        "_op_type": "index",
        "_index": "products",
        "_type": "product",
        "_id": 33000006,
        "_source": {
          "long_product_description": "this the the longer",
          "end_date": None,
          "product_url": "http://example.com",
          "color": "blue",
          "gender": "MEN",
          "keywords": "",
          "begin_date": None,
          "discount": 0,
          "created_at": None,
          "merchant_id": 13816,
          "product_image_url": "lol",
          "availability": "in-stock",
          "retail_price": 388,
          "is_trending": False,
          "is_deleted": False,
          "updated_at": "2018-01-30T04:42:37.000Z",
          "primary_category": "Apparel & Accessories",
          "product_id": 1000007,
          "short_product_description": "shorter",
          "@version": "1",
          "currency": "USD",
          "id": 230000000,
          "sku": "13058br9nch9mp",
          "brand": "Reformation",
          "is_best_seller": False,
          "shipping_price": 0,
          "merchant_color": "August",
          "raw_product_url": "derived",
          "buy_url": "",
          "merchant_name": "Reformation",
          "allume_size": None,
          "manufacturer_name": "Reformation",
          "discount_type": "amount",
          "product_name": "Thistle Dress Mk45",
          "sale_price": 0,
          "secondary_category": "Clothing~~Dresses",
          "product_type": "",
          "@timestamp": "2018-02-08T04:18:02.210Z",
          "size": "4P",
          "material": "",
          "manufacturer_part_number": "1301882CHR",
          "style": "",
          "current_price": 388,
          "allume_category": "Dresses",
          "allume_score": 0,
          "age": "ADULT"
        }
      },
      {
        "_op_type": "index",
        "_index": "products",
        "_type": "product",
        "_id": 33000007,
        "_source": {
          "long_product_description": "this the the longer",
          "end_date": None,
          "product_url": "http://example.com",
          "color": "blue",
          "gender": "MEN",
          "keywords": "",
          "begin_date": None,
          "discount": 0,
          "created_at": None,
          "merchant_id": 13816,
          "product_image_url": "lol",
          "availability": "in-stock",
          "retail_price": 388,
          "is_trending": False,
          "is_deleted": False,
          "updated_at": "2018-01-30T04:42:37.000Z",
          "primary_category": "Apparel & Accessories",
          "product_id": 1000008,
          "short_product_description": "shorter",
          "@version": "1",
          "currency": "USD",
          "id": 230000000,
          "sku": "13058br9nch9mp",
          "brand": "Reformation",
          "is_best_seller": False,
          "shipping_price": 0,
          "merchant_color": "August",
          "raw_product_url": "derived",
          "buy_url": "",
          "merchant_name": "Reformation",
          "allume_size": None,
          "manufacturer_name": "Reformation",
          "discount_type": "amount",
          "product_name": "Thistle Dress Mk45",
          "sale_price": 0,
          "secondary_category": "Clothing~~Dresses",
          "product_type": "",
          "@timestamp": "2018-02-08T04:18:02.210Z",
          "size": "4P",
          "material": "",
          "manufacturer_part_number": "1301882CHR",
          "style": "",
          "current_price": 388,
          "allume_category": "Dresses",
          "allume_score": 0,
          "age": "ADULT"
        }
      },
      {
        "_op_type": "index",
        "_index": "products",
        "_type": "product",
        "_id": 33000008,
        "_source": {
          "long_product_description": "this the the longer",
          "end_date": None,
          "product_url": "http://example.com",
          "color": "blue",
          "gender": "MEN",
          "keywords": "",
          "begin_date": None,
          "discount": 0,
          "created_at": None,
          "merchant_id": 13816,
          "product_image_url": "lol",
          "availability": "in-stock",
          "retail_price": 388,
          "is_trending": False,
          "is_deleted": False,
          "updated_at": "2018-01-30T04:42:37.000Z",
          "primary_category": "Apparel & Accessories",
          "product_id": 1000009,
          "short_product_description": "shorter",
          "@version": "1",
          "currency": "USD",
          "id": 230000000,
          "sku": "13058br9nch9mp",
          "brand": "Reformation",
          "is_best_seller": False,
          "shipping_price": 0,
          "merchant_color": "August",
          "raw_product_url": "derived",
          "buy_url": "",
          "merchant_name": "Reformation",
          "allume_size": None,
          "manufacturer_name": "Reformation",
          "discount_type": "amount",
          "product_name": "Thistle Dress Mk45",
          "sale_price": 0,
          "secondary_category": "Clothing~~Dresses",
          "product_type": "",
          "@timestamp": "2018-02-08T04:18:02.210Z",
          "size": "4P",
          "material": "",
          "manufacturer_part_number": "1301882CHR",
          "style": "",
          "current_price": 388,
          "allume_category": "Dresses",
          "allume_score": 0,
          "age": "ADULT"
        }
      },
      {
        "_op_type": "index",
        "_index": "products",
        "_type": "product",
        "_id": 33000009,
        "_source": {
          "long_product_description": "this the the longer",
          "end_date": None,
          "product_url": "http://example.com",
          "color": "blue",
          "gender": "MEN",
          "keywords": "",
          "begin_date": None,
          "discount": 0,
          "created_at": None,
          "merchant_id": 13816,
          "product_image_url": "lol",
          "availability": "in-stock",
          "retail_price": 388,
          "is_trending": False,
          "is_deleted": False,
          "updated_at": "2018-01-30T04:42:37.000Z",
          "primary_category": "Apparel & Accessories",
          "product_id": 1000010,
          "short_product_description": "shorter",
          "@version": "1",
          "currency": "USD",
          "id": 230000000,
          "sku": "13058br9nch9mp",
          "brand": "Reformation",
          "is_best_seller": False,
          "shipping_price": 0,
          "merchant_color": "August",
          "raw_product_url": "derived",
          "buy_url": "",
          "merchant_name": "Reformation",
          "allume_size": None,
          "manufacturer_name": "Reformation",
          "discount_type": "amount",
          "product_name": "Thistle Dress Mk45",
          "sale_price": 0,
          "secondary_category": "Clothing~~Dresses",
          "product_type": "",
          "@timestamp": "2018-02-08T04:18:02.210Z",
          "size": "4P",
          "material": "",
          "manufacturer_part_number": "1301882CHR",
          "style": "",
          "current_price": 388,
          "allume_category": "Dresses",
          "allume_score": 0,
          "age": "ADULT"
        }
      }
    ]

    helpers.bulk(client, actions)





def attempt_to_add_a_doc():
    client.index(index='products', doc_type='product', id = 33000000, body={
      "long_product_description": "this the the longer",
      "end_date": None,
      "product_url": "http://example.com",
      "color": "blue",
      "gender": "MEN",
      "keywords": "",
      "begin_date": None,
      "discount": 0,
      "created_at": None,
      "merchant_id": 40090,
      "product_image_url": "lol",
      "availability": "in-stock",
      "retail_price": 388,
      "is_trending": False,
      "is_deleted": False,
      "updated_at": "2018-01-30T04:42:37.000Z",
      "primary_category": "Apparel & Accessories",
      "product_id": 112323564564534,
      "short_product_description": "shorter",
      "@version": "1",
      "currency": "USD",
      "id": 230000000,
      "sku": "13058br9nch9mp",
      "brand": "Reformation",
      "is_best_seller": False,
      "shipping_price": 0,
      "merchant_color": "August",
      "raw_product_url": "derived",
      "buy_url": "",
      "merchant_name": "Reformation",
      "allume_size": None,
      "manufacturer_name": "Reformation",
      "discount_type": "amount",
      "product_name": "Thistle Dress Mk35",
      "sale_price": 0,
      "secondary_category": "Clothing~~Dresses",
      "product_type": "",
      "@timestamp": "2018-02-08T04:18:02.210Z",
      "size": "4P",
      "material": "",
      "manufacturer_part_number": "1301882CHR",
      "style": "",
      "current_price": 388,
      "allume_category": "Dresses",
      "allume_score": 0,
      "age": "ADULT"
        })

def attempt_delete_a_doc():
    client.delete(index='products', doc_type='product', id=33000000)

# index example
# es.index(index='test_index', doc_type='post', id=1, body={
#   'author': 'John Doe',
#   'blog': 'Learning Elasticsearch',
#   'title': 'Using Python with Elasticsearch',
#   'tags': ['python', 'elasticsearch', 'tips'],
# })

# create fake index maybe loool?


# _id fields are delivered as part of response, we can potentially make a bulk delete pretty simply?
def understand_documents():
# document get example
# es.get(index='test_index', id='1')
    response = client.get(index="products", id='33000000')
    print response



def attempt_using_espy():

    response = client.search(
        index="products",
        body={
          "query": {
            "bool": {
              "must": [
              { "match": { "product_id": "3355592380" }},
              { "match": { "merchant_id": "41754" }}
              ]
            }
          }
        }
    )

    # attempt at using bulk
    # actions = ? 
    bulk(client, actions)

    print response

    for hit in response['hits']['hits']:
        print hit

def attempt_bulk_delete():
    actions = [
      {
        '_op_type': 'delete',
        '_index': 'products',
        '_type': 'product',
        '_id': 33000000
      },
      {
        '_op_type': 'delete',
        '_index': 'products',
        '_type': 'product',
        '_id': 33000001
      }
    ]

    helpers.bulk(client, actions)


# attempt to rewrite the task of interest
def attempt_product_index_delete_via_bulk(days_threshold = 5):
    """
    Any other concerns about where this method might fail?
    """
    datetime_threshold = datetime.now() - timedelta(days = days_threshold) # query products as far back as days_threshold
    deleted_products = Product.objects.filter(updated_at__gte = datetime_threshold, is_deleted = True)
    deleted_products = deleted_products.values_list('product_id', 'merchant_id') # ids are longs

    print len(deleted_products)

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


    print len(document_ids)
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
    helpers.bulk(client, actions)

# response['hits']['hits'] is a list of hits...
# when we match exactly, we will only get 1 or 0 hits
# can we construct a query st we get a list of all prod_id, merchant_id pairs of interest?


# document_id = response['hits']['hits'][0]['_id']
# document id is what is used in the es index, can then compile a list of these and delete via bulk?

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

