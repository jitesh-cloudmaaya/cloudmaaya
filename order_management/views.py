# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
import requests
from django.shortcuts import redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from django.db import connection
from django.utils import timezone
import urllib2

import json

from catalogue_service.settings import STYLING_SERVICES_STAGE, STYLING_SERVICES_PROD, ENV_LOCAL

# server the check final sale page
def final_sale_check(requests, allume_cart_id):
    context = {'allume_cart_id': allume_cart_id}
    return render(requests, 'final_sale_check/index.html', context)

# a proxy for the frontend to access product website
# To Do
# need to resovle the relative paths in the front end iframe
def proxy(request):
    url = request.GET['url']
    url = urllib2.unquote(url)
    response = requests.get(url)
    response.headers['X-Frame-Options'] = 'ALLOWALL' # allow iframe
    response.headers['Access-Control-Allow-Origin'] = '*'
    return HttpResponse(response)

# load the check final sale data to front end
def get_unchecked_final_sale_data(requests):
    allume_cart_id = requests.GET['allume_cart_id']
    data = load_uncheck_final_sale_data(allume_cart_id)
    return JsonResponse(data)

# after all the items are checked, front end calls this API to submit data
@csrf_exempt
def submit_final_sale_check(requests):
    data = json.loads(requests.body)
    allume_cart_id = data['allume_cart_id']
    if data['allume_cart_id'] and data['items']: # only update when there is valid information in the result
        
        all_orders = set()
        final_sale_orders = set()

        # process final sale check data
        for item in data['items']:
            all_orders.add(data['items'][item]['order_id']) # add an order to all order set
            if data['items'][item]['final_sale']: # if not final sale
                set_final_sale(item, True)
                final_sale_orders.add(data['items'][item]['order_id']) # add an order to final sale order
            else:   # if final sale
                set_final_sale(item, False)

        # check all items are processed
        if not load_uncheck_final_sale_data(allume_cart_id):

            # order handling
            for order_id in all_orders:
                if order_id in final_sale_orders: # this order has final sale
                    onhold_retailer_order(order_id)
                else:  # this order has no final sale
                    approve_retailer_order(order_id)

            # check if any final sale order -> yes> send text or no> start order
            if final_sale_orders:
                # message handling
                # call the text queue API
                # api_call_to_message_queue
                api_call_to_message_queue(allume_cart_id)
            else:
                # start order 
                # call the start order API
                api_call_to_start_order(allume_cart_id)

            # TODO
            # api_call_to_delete_order_job(allume_cart_id)
            api_call_to_delete_order_job(allume_cart_id)

    return HttpResponse(status=200)

################################
# Message Handling
################################
def api_call_to_message_queue(allume_cart_id, message_content = None):

    # send request to the styling service API
    if ENV_LOCAL == 'prod':
        url = STYLING_SERVICES_PROD + 'push_message_api/'
    elif ENV_LOCAL == 'stage':
        url = STYLING_SERVICES_STAGE + 'push_message_api/'

    # construct data in json format
    json_data = {
        'allume_cart_id': allume_cart_id,
        'message_content': message_content
    }
    r = requests.post(url, json=json_data)

    # return True/False to indicate if the request is successful
    if r.status_code == 200:
        return True
    else:
        return False

def api_call_to_delete_order_job(allume_cart_id):

    # send request to the styling service APIQ
    if ENV_LOCAL == 'prod':
        url = STYLING_SERVICES_PROD + 'delete_order_job_api/'
    elif ENV_LOCAL == 'stage':
        url = STYLING_SERVICES_STAGE + 'delete_order_job_api/'

    # construct data in json format
    json_data = {
        'allume_cart_id': allume_cart_id
    }
    r = requests.post(url, json=json_data)

    # return True/False to indicate if the request is successful
    if r.status_code == 200:
        return True
    else:
        return False


def api_call_to_start_order(allume_cart_id):
    # send request to the styling service APIQ
    if ENV_LOCAL == 'prod':
        url = STYLING_SERVICES_PROD + 'start_order/'
    elif ENV_LOCAL == 'stage':
        url = STYLING_SERVICES_STAGE + 'start_order/'

    # construct data in json format
    json_data = {
        'allume_cart_id': allume_cart_id
    }
    r = requests.post(url, json=json_data)
    
    # return True/False to indicate if the request is successful
    if r.status_code == 200:
        return True
    else:
        return False

###############################################
# Order Handling (should be API calls as wll)
###############################################
# onhold an order
# <2> onhold a particular retailer order (wp_post shop order) & disapprove them as well
def onhold_retailer_order(wp_post_order_id):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            update wp_posts
            set post_status = %s, approved = 0
            where ID = %s
            """
            , ['wc-on-hold', wp_post_order_id]
        )
        return 

def approve_retailer_order(retailer_order_id):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            update wp_posts
            set approved = true
            where ID = %s
            """
            , [retailer_order_id,]
        )
        return

################################
# SQL Helper
################################
def load_uncheck_final_sale_data(allume_cart_id):
    item_ids = get_unchecked_final_sale_item_ids_by_allume_cart_id(allume_cart_id)
    number_of_items = len(item_ids)
    data = {}
    if number_of_items:
        data['number_of_items'] = number_of_items
        current_item_rank = 1
        for item_id in item_ids:
            url, detail = get_final_sale_detail(item_id[0])
            data[current_item_rank] = {}
            data[current_item_rank]['item_id'] = item_id[0]
            data[current_item_rank]['order_id'] = item_id[1]
            data[current_item_rank]['url'] = url
            data[current_item_rank]['detail'] = detail
    return data

# get item ids by allume_cart_id
def get_unchecked_final_sale_item_ids_by_allume_cart_id(allume_cart_id):
    # get all order_item_id
    with connection.cursor() as cursor:
        cursor.execute(
            """
            select order_item_id, order_id
            from
            (select order_item_id, order_id
            from
            (select M.ID
            from
            (select ID, retailer
            from wp_posts
            where allume_cart_id = %s and approved=false 
            and post_status!='wc-completed' and post_status!='wc-cancelled' and (twotap_processing_status is null or twotap_processing_status='failed')) as M
            join product_api_merchant
            on M.retailer = product_api_merchant.name
            where final_sale=true
            group by M.ID)
            as O
            join
            wp_woocommerce_order_items
            on O.ID = wp_woocommerce_order_items.order_id
            where order_item_type='line_item') as I
            where
            not exists (select * from wp_woocommerce_order_itemmeta where order_item_id=I.order_item_id and meta_key='_final_sale')
            """,
            [allume_cart_id,] #15355
        )
        # create a list of item_ids
        cursor_item_ids = cursor.fetchall()
        item_ids = []
        for cursor_item in cursor_item_ids:
            # [0] is item_id, [1] is order_id
            item_id = cursor_item[0]
            order_id = cursor_item[1]
            item_ids.append([item_id, order_id]) 
        return item_ids

# get detail information about an item
def get_final_sale_detail(order_item_id):
    with connection.cursor() as cursor:
        # get link
        cursor.execute(
            """
            select meta_value
            from wp_woocommerce_order_itemmeta
            where order_item_id = %s and meta_key = 'affiliate_link';
            """,
            [order_item_id,]
        )
        link = cursor.fetchone()[0]
        # get variation info
        cursor.execute(
            """
            select meta_value
            from wp_woocommerce_order_itemmeta
            where order_item_id = %s and meta_key = 'variation_info';
            """,
            [order_item_id,]
        )
        detail = cursor.fetchone()[0]
        return (link, detail)

# set an item as final sale
def set_final_sale(order_item_id, is_final_sale):
    with connection.cursor() as cursor:
        # set true
        if is_final_sale:
            cursor.execute(
                """
                insert into wp_woocommerce_order_itemmeta (order_item_id, meta_key, meta_value)
                values (%s, '_final_sale', true)
                """,
                [order_item_id,]
            )
            cursor.execute(
                """
               update product_api_product pp
                   join wp_posts p on p.affiliate_feed_product_api_product_id = pp.id
                   join wp_woocommerce_order_itemmeta oim on oim.order_item_id = %s and oim.meta_key='_product_id' and oim.meta_value = p.ID
                   set pp.is_final_sale = 1, pp.updated_at = now()
                """,
                [order_item_id,]
            )
        # set false
        else:
            cursor.execute(
                """
                insert into wp_woocommerce_order_itemmeta (order_item_id, meta_key, meta_value)
                values (%s, '_final_sale', false)
                """,
                [order_item_id,]
            )




    