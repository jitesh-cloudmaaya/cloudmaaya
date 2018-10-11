# -*- coding: utf-8 -*-
"""
This is the data analytic codes to process the raw data in look copy tracing table
It suppose to run once a day
"""
import csv
import json
from shopping_tool.models import LookCopy, Look, WpUsers, LookProduct
from product_api.models import Merchant, Product
from catalogue_service.settings_local import ENV_LOCAL, AWS_ACCESS_KEY, AWS_SECRET_KEY
import boto3
import os
import datetime

def analyze_data():

    # define header
    header = ['from_look_id', 'to_look_id', 'from_look_name', 'from_look_url', 'to_look_name', 'to_look_url', 'from_stylist_id', 'from_stylist_name', 'from_stylist_email','to_stylist_id', 'to_stylist_name', 'to_stylist_email','addition', 'addition_count', 'subtraction', 'subtraction_count', 'change_count', 'last_updated']
    time_stamp = str(datetime.datetime.now())
    time_stamp_row = ['', '', '', '', '', '', '', '', '','', '', '','', '', '', '', '', time_stamp]
    all_copies = LookCopy.objects.all()
    # open file
    with open('look_copy_report.csv', mode='wb') as report_file:
        report_writer = csv.writer(report_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        report_writer.writerow(header) # add header
        report_writer.writerow(time_stamp_row) # time stamp

        # loop
        for copy in all_copies:

            # check if a new look is alreay published
            to_look_id = copy.to_look_id
            to_look = Look.objects.get(id=to_look_id)
            if to_look.status == 'published':

                # rest of look details
                from_look_id = copy.from_look_id
                from_look = Look.objects.get(id=from_look_id)
                from_look_name = from_look.name
                to_look_name = to_look.name

                # basic information
                from_stylist_id = copy.from_stylist_id
                to_stylist_id = copy.to_stylist_id
                from_stylist = WpUsers.objects.get(id=from_stylist_id)
                to_stylist = WpUsers.objects.get(id=to_stylist_id)
                from_stylist_name = from_stylist.first_name + ' ' + from_stylist.last_name
                to_stylist_name = to_stylist.first_name + ' ' + to_stylist.last_name
                from_stylist_email = from_stylist.user_email
                to_stylist_email = to_stylist.user_email

                # check product addition and subtraction
                addition = []
                addition_count = 0
                subtraction = []
                subtraction_count = 0
                old_look_products = json.loads(copy.old_look_snapshot)

                # generate different lookbook urls for stage or production. Caution! Hardcoded Url!
                if ENV_LOCAL == 'prod':
                    prefix = 'https://www.allume.co/looks/%s'
                else:
                    prefix = 'https://stage.allume.co/looks/%s'
                from_look_url = prefix % from_look.allume_styling_session.token
                to_look_url = prefix % to_look.allume_styling_session.token

                # check new look items
                new_look_products_set = LookProduct.objects.filter(look_id=to_look_id)
                new_look_products = []
                for look_product in new_look_products_set:
                    new_look_products.append(look_product.product_id)
                
                # check addition
                for product in new_look_products:
                    if product not in old_look_products:
                        addition.append(product)
                        addition_count += 1
                # check subtraction
                for product in old_look_products:
                    if product not in new_look_products:
                        subtraction.append(product)
                        subtraction_count += 1
                
                # number of changes
                change_count = addition_count + subtraction_count

                # write to file
                report_writer.writerow([from_look_id, to_look_id, 
                from_look_name.encode('utf-8'), from_look_url, to_look_name.encode('utf-8'), to_look_url,
                from_stylist_id, from_stylist_name.encode('utf-8'), from_stylist_email, 
                to_stylist_id, to_stylist_name.encode('utf-8'), to_stylist_email, 
                addition, addition_count, subtraction, subtraction_count, change_count])

    # upload csv to S3
    if ENV_LOCAL == 'prod':
        upload_key = 'prod/looks-copy/look_copy_report.csv' # get the upload key to upload to S3
    else:
        upload_key = 'stage/looks-copy/look_copy_report.csv'
    data = open('look_copy_report.csv', 'rb')
    client = boto3.client('s3',aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
    client.put_object(Body=data, Bucket='allume-reports', Key=upload_key)

    # delete the local file
    os.remove('look_copy_report.csv')