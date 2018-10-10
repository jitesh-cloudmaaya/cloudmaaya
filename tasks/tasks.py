from __future__ import absolute_import, unicode_literals
from celery import task, shared_task
from django.db import connection, transaction
import os
import time
from catalogue_service.settings import BASE_DIR, SLACK_BASE_URL, SLACK_IDENTIFIER
from celery_once import QueueOnce
from product_api.models import Product, AllumeCategory, CategoryMap, Merchant
from tasks.product_feed import ProductFeed
from tasks.product_feed_py.pepperjam import get_data, get_merchants
from datetime import datetime, timedelta
from elasticsearch_dsl import Search
from catalogue_service.settings import * # for the ES connection
from elasticsearch import Elasticsearch, helpers

from .lookcopy_trace.analysis import analyze_data

import requests
import json

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
    print("Now setting deleted for non-upserted products")
    pf.set_deleted_network_products()
    print("Successfully set non-upserted products to deleted")

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
    # TO-DO: handling the deleted call for delta files

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
    print("Now setting deleted for non-upserted products")
    pf.set_deleted_network_products()
    print("Successfully set non-upserted products to deleted")

@task(base=QueueOnce)
def impact_radius_pull():
    pf = ProductFeed(os.path.join(BASE_DIR, 'catalogue_service/impact_radius.yaml'))
    print("Pulling files from FTP")
    pf.get_files_ftp()
    print("Decompressing files")
    pf.decompress_data()
    print("Cleaning files")
    pf.clean_data()
    print("Update API products table")
    pf.load_cleaned_data()
    print("Sucessfully updated API products table")
    print("Now setting deleted for non-upserted products")
    pf.set_deleted_network_products()
    print("Successfully set non-upserted products to deleted")

@task(base=QueueOnce)
def cj_pull():
    pf = ProductFeed(os.path.join(BASE_DIR, 'catalogue_service/cj.yaml'))
    print("Pulling files from FTP")
    pf.get_files_sftp()
    print("Decompressing files")
    pf.decompress_data()
    print("Cleaning files")
    pf.clean_data()
    print("Update API products table")
    pf.load_cleaned_data()
    print("Successfully updated API products table")
    print("Now setting deleted for non-upserted products")
    pf.set_deleted_network_products()
    print("Successfully set non-upserted products to deleted")

@task(base=QueueOnce)
def build_client_360():
    add_client_to_360_raw('tasks/client_360_sql/client_360.sql', {'user_filter': ';', 'quiz_answer_user_filter_and_clause': '', 'quiz_answer2_user_filter_and_clause': ''})

#
# @task(base=QueueOnce)
# def update_client_360():
#     add_client_to_360_raw('tasks/client_360_sql/update_client_360.sql',
#                           'WHERE wu.id IN (SELECT u0.ID FROM wp_users u0 WHERE u0.last_modified > (SELECT MAX(a0.last_updated) FROM allume_client_360 a0));')


@shared_task
def add_client_to_360(wp_user_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            DELETE from allume_client_360 WHERE wp_user_id = %s
        """, [wp_user_id])
    with connection.cursor() as cursor:
        cursor.execute("""
            select user_email from wp_users WHERE ID = %s
        """, [wp_user_id])
        email = cursor.fetchone()[0]
    add_client_to_360_raw(
        'tasks/client_360_sql/client_360_one.sql'
        , {
            'user_filter': 'where wu.id = ' + str(wp_user_id) + ';'
            , 'quiz_answer_user_filter_and_clause': ' and qua.user_email = "' + email + '" '
            , 'quiz_answer2_user_filter_and_clause': ' and qua2.user_email = "' + email + '" '
        }
    )


def add_client_to_360_raw(task_sql, user_filters):
    from django.db import connections
    user_filters = user_filters if user_filters else {}
    cursor = connection.cursor()
    etl_read_file = open(os.path.join(BASE_DIR, 'tasks/client_360_sql/client_360_read.sql'))
    etl_file = open(os.path.join(BASE_DIR, task_sql))
    read_statement = etl_read_file.read()
    read_statement = read_statement.replace('$USER_FILTER', user_filters.get('user_filter') if user_filters.get('user_filter') else ';')
    read_statement = read_statement.replace('$QUIZ_ANSWER_USER_FILTER_AND_CLAUSE', user_filters.get('quiz_answer_user_filter_and_clause') if user_filters.get('quiz_answer_user_filter_and_clause') else '')
    read_statement = read_statement.replace('$QUIZ_ANSWER2_USER_FILTER_AND_CLAUSE', user_filters.get('quiz_answer2_user_filter_and_clause') if user_filters.get('quiz_answer2_user_filter_and_clause') else '')
    quiz_orders_data = []
    try:
        read_statements = read_statement.split(';')
        for i in range(0, len(read_statements)):
            read_statement = read_statements[i]
            if read_statement.strip():  # avoid 'query was empty' operational error
                with connections['allume_read_only'].cursor() as read_cursor:
                    read_cursor.execute(read_statement)
                    quiz_orders_data = read_cursor.fetchall()
        statement = etl_file.read()
        statements = statement.split(';')
        with transaction.atomic():
            for i in range(0, len(statements)):
                statement = statements[i]
                if statement.strip():  # avoid 'query was empty' operational error
                    if 'insert into' in statement.lower():
                        cursor.executemany(statement, quiz_orders_data)
                    else:
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

    # sql to set inactive products to deleted
    product_table = Product._meta.db_table
    categorymap_table = CategoryMap._meta.db_table
    merchant_table = Merchant._meta.db_table
    allumecategory_table = AllumeCategory._meta.db_table

    statement1 = 'UPDATE %s pap' % product_table
    statement1 += ' INNER JOIN %s pac ON pap.primary_category = pac.external_cat1' % categorymap_table
    statement1 += ' AND pap.secondary_category = pac.external_cat2'
    statement1 += ' SET is_deleted = 1 AND pap.updated_at = NOW() WHERE pac.active = 0 and pap.is_deleted != 1'

    statement2 = 'UPDATE %s pap' % product_table
    statement2 += ' INNER JOIN %s pam ON pap.merchant_id = pam.external_merchant_id' % merchant_table
    statement2 += ' SET is_deleted = 1 AND pap.updated_at = NOW() WHERE pam.active = 0 and pap.is_deleted != 1'

    statement3 = 'UPDATE %s pap' % product_table
    statement3 += ' INNER JOIN %s paa ON pap.allume_category = paa.name' % allumecategory_table
    statement3 += ' SET is_deleted = 1 AND pap.updated_at = NOW() WHERE paa.active = 0 and pap.is_deleted != 1'


    with connection.cursor() as cursor:
        cursor.execute(statement1)
        print 'Setting the inactive products to deleted took %s seconds' % (time.time() - start)
        cursor.execute(statement2)
        print 'Setting the inactive products to deleted took %s seconds' % (time.time() - start)
        cursor.execute(statement3)
        cursor.close()

    print 'Setting the inactive products to deleted took %s seconds' % (time.time() - start)

    checkpoint = time.time()

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

    print 'Removing deleted products from the index took %s seconds' % (time.time() - checkpoint)

    print 'The entire process took %s seconds' % (time.time() - start)


###########################################
#   Look copy analytic
###########################################
@task(base=QueueOnce)
def generate_look_copy_report():
    print('look copy data analyzation started')
    analyze_data()
    print('look copy data is analyzed and a report is ready for download')

####################################################
#   Merchant last product update report and warning
####################################################

# function to send slack message
def send_slack_notification(channel, message):

    slack_data = {
        'channel': channel,
        'text': message,
        'username': 'concierge',
        'icon_emoji': ':allume-logo:'
    }

    response = requests.post(
        SLACK_BASE_URL + SLACK_IDENTIFIER,
        data=json.dumps(slack_data),
        headers={'Content-Type': 'application/json'}
    )

    if response.status_code == 200:
        return True
    else:
        return False

# task to calculate the most recent product update of each merchant and sends slack message 
# if no product from this merchant has been updated for a given number of days
@task(base=QueueOnce)
def check_merchant_last_update(days_threshold = 3):
    print('start checking the most recent update of each merchant')
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT name, max(P.updated_at) FROM
        product_api_merchant AS M
        INNER JOIN 
        product_api_product AS P
        WHERE M.external_merchant_id = P.merchant_id
        GROUP BY M.external_merchant_id;
        """
    ) 
    
    # loop
    current_time = datetime.now()
    message = ''
    for item in cursor:
        last_updated_time = item[1] # the fourth element based on the SQL query
        diff = current_time - last_updated_time # calculate the diff b/w 
        if diff.days > days_threshold:
            message += '\n name: ' + str(item[0]) + '\n last_updated: ' + str(item[1]) + '\n\n'

    # check if any message
    if message:
        prefix = '\n WARNING: The following merchants have NOT updated their products for a while \n\n'
        message = prefix + message
        send_slack_notification('anna_tasks_failures', message) # send slack message to anna_tasks_failures channel

    else:
        print('check performed, all merchants have product updated recently')
        return