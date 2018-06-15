import os
import datetime
import yaml
import json
import urllib2
import urlparse
import csv
import time
import re
from copy import copy
from django.db import connection
from tasks.product_feed_py import mappings, product_feed_helpers
from catalogue_service.settings import BASE_DIR, PEPPERJAM_API_VERSION, PEPPERJAM_API_KEY
from product_api.models import CategoryMap, Network, Merchant, Product, SynonymCategoryMap, ExclusionTerm
from datetime import datetime, timedelta

# Set Up PepeprJam URL
PEPPER_JAM_API_BASE_URL = "https://api.pepperjamnetwork.com/%s/" % (PEPPERJAM_API_VERSION)

def get_merchants(status='joined', dev=False):

    # Set Up PepperJam URL
    pepper_jam_api_merchant_url = PEPPER_JAM_API_BASE_URL + "publisher/advertiser?apiKey=%s&status=%s&format=json" % (PEPPERJAM_API_KEY, status)

    # Look Up Existing DB Meta Data
    merchant_mapping = mappings.create_merchant_mapping()
    network = mappings.get_network('PepperJam')

    ## Dev Only
    # # Test Merchants Data
    if dev:
        print("Getting local test data")
        json_data = open('tasks/product_feed_py/sample_data/pepperjam_merchant.json')
        merchants = json.load(json_data)
        json_data.close()

    # Get Merchants
    ## Prod & Staging Only
    else:
        print 'Getting merchants using API call'

        # set api call variables
        numTries = 4 # total number of tries
        timeout = 60 # in seconds
        delay = 3 # pause in seconds between retries
        backoff = 2 # multiplier on timeout between retries

        json_data = open_w_timeout_retry(pepper_jam_api_merchant_url, numTries, timeout, delay, backoff)
        merchants = json.load(json_data)
    
    # Create some variables to count process metrics
    new_merchants = 0

    for merchant in merchants['data']:
        merchant_id = long(merchant['id'])
        merchant_name = merchant['name']

        if merchant_id not in merchant_mapping.keys():
            # create new merchant in django/db
            mappings.add_new_merchant(merchant_id, merchant_name, network, False)
            new_merchants += 1

    print('Added %s new merchants' % new_merchants)

    merchant_mapping = mappings.create_merchant_mapping() # reload mapping to reflect new merchants
    return merchant_mapping

def get_data(local_temp_dir, cleaned_fieldnames, dev=False):

     # Set Up PepperJam URL
    pepper_jam_api_product_url = PEPPER_JAM_API_BASE_URL + "publisher/creative/product?apiKey=%s&format=json" % (PEPPERJAM_API_KEY)
    #pepper_jam_api_product_url = "https://api.pepperjamnetwork.com/20120402/publisher/creative/product?apiKey=48db78a072444a019989822d21aa513a5f0f67bb2363d6370b9e59b23bd4b29d&format=json&page=26"

    # Get Mapping Data
    merchant_mapping = get_merchants(status='joined',dev=dev) # new way to create merchant_mapping?
    merchant_search_rank_mapping = mappings.create_merchant_search_rank_mapping()
    color_mapping = mappings.create_color_mapping()
    category_mapping = mappings.create_category_mapping()
    allume_category_mapping = mappings.create_allume_category_mapping()
    size_mapping = mappings.create_size_mapping()
    shoe_size_mapping = mappings.create_shoe_size_mapping()
    size_term_mapping = mappings.create_size_term_mapping()
    synonym_category_mapping = mappings.create_synonym_category_mapping()
    synonym_other_category_mapping = mappings.create_synonym_other_category_mapping()
    known_text_sizes, known_number_sizes = mappings.create_retailer_size_mappings()

    # for use when adding a mapping
    exclusion_terms = mappings.create_exclusion_term_mapping()
    synonym_other_terms = SynonymCategoryMap.objects.filter(category = 'Other').values_list('synonym', flat=True)
    synonym_terms = SynonymCategoryMap.objects.values_list('category', flat=True)


    network = mappings.get_network('PepperJam')

    # Set Up PepeprJam URL
    pepper_jam_api_base_url = "https://api.pepperjamnetwork.com/%s/" % (PEPPERJAM_API_VERSION)
    pepper_jam_api_product_url = pepper_jam_api_base_url + "publisher/creative/product?apiKey=%s&format=json" % (PEPPERJAM_API_KEY)

    # Set output Destination
    destination = local_temp_dir + '/ppj_flat_file.csv'
    print destination
    # Create some variables to count process metrics
    totalCount = 0
    writtenCount = 0
    genderSkipped = 0
    categoriesSkipped = 0
    categoryCount = CategoryMap.objects.count()

    with open(destination, "w") as cleaned:
        # first guess at dialect
        csv.register_dialect('writing', delimiter=',', quoting=csv.QUOTE_ALL, quotechar='"', doublequote=False, escapechar='\\', lineterminator='\n')
        # cleaned_fieldnames const until can pass in yaml

        cleaned_fieldnames = cleaned_fieldnames.split(',')
        # intiialize the csv wrtier
        writer = csv.DictWriter(cleaned, cleaned_fieldnames, dialect = 'writing')

        more_pages = True

        while more_pages:
            ## Dev Only
            if dev:
                print("Getting Data")
                print(pepper_jam_api_product_url)
                json_data = open('tasks/product_feed_py/sample_data/pepperjam_product.json')
                product_feed = json.load(json_data)
                json_data.close()

            # commenting out because API only has X amount of access allowed in a day
            ## Prod & Staging Only
            else:
                print 'Getting data using the API calls'
                print("Getting Data")

                # set api call variables
                numTries = 4 # total number of tries
                timeout = 60 # in seconds
                delay = 3 # pause in seconds between retries
                backoff = 2 # multiplier on timeout between retries

                print(pepper_jam_api_product_url)
                json_data = open_w_timeout_retry(pepper_jam_api_product_url, numTries, timeout, delay, backoff)
                product_feed = json.load(json_data)


            if 'next' in product_feed['meta']['pagination']:
                pepper_jam_api_product_url = product_feed['meta']['pagination']['next']['href']
            else:
                more_pages = False

            for product in product_feed['data']:

                merchant_id = product['program_id']
                merchant_name = product['program_name']


                # Test if Mechant Is Active
                try:
                    # update if merchant is active, should always have entry
                    merchant_is_active = merchant_mapping[long(merchant_id)]
                except KeyError:
                    print 'somehow used a merchant_id not present in the mapping'
                    continue
                # check that the merchant_id is active in the merchant mapping
                if merchant_is_active == False:
                    continue

                # config files
                config_path = BASE_DIR + '/tasks/product_feed_py/merchants_config/pepperjam/'
                fd = os.listdir(config_path)
                default = 'default'
                extension = '.yaml'
                default_filename = default + extension
                merchant_id_filename = str(merchant_id) + extension

                full_path = config_path + default_filename

                if merchant_id_filename in fd:
                    full_path = config_path + merchant_id_filename

                with open(full_path, "r") as config:
                    config_dict = yaml.load(config)
                    try:
                        tiered_assignments = config_dict['tiered_assignment_fields']
                    except KeyError:
                        tiered_assignments = {}

                primary_category = product['category_program']
                # secondary_category = product['category_network']
                secondary_category = product_feed_helpers.product_field_tiered_assignment(tiered_assignments, 'secondary_category', product, product['category_network'], synonym_category_mapping = synonym_category_mapping, synonym_other_category_mapping = synonym_other_category_mapping, exclusion_terms = exclusion_terms)

                allume_category = mappings.are_categories_active(primary_category, secondary_category, category_mapping, allume_category_mapping, merchant_name, exclusion_terms, synonym_other_terms, synonym_terms)
                # allume_category = 'allume_category' # include to overrule category activity checks

                if allume_category:
                    record = {}
                    record['merchant_id'] = merchant_id
                    record['product_name'] = product['name'] # product_name
                    record['long_product_description'] = product['description_long']
                    record['short_product_description'] = product['description_short']
                    buy_url = product['buy_url']
                    record['product_url'] = buy_url # product_url == buy_url?
                    try:
                        record['raw_product_url'] = product_feed_helpers.parse_raw_product_url(buy_url, 'url')
                    except KeyError as e:
                        print e
                        record['raw_product_url'] = u''
                    # record['raw_product_url'] = urlparse.parse_qs(urlparse.urlsplit(buy_url).query)['url'][0]
                    record['product_image_url'] = product['image_url']
                    record['buy_url'] = buy_url
                    record['manufacturer_name'] = product['manufacturer']
                    record['manufacturer_part_number'] = product['mpn']
                    record['SKU'] = product['sku']

                    product_id = generate_product_id_pepperjam(product['sku'], merchant_id)
                    # print product_id
                    # print type(product_id)
                    record['product_id'] = product_id

                    record['product_type'] = u'attribute_2_product_type'

                    discount_type = '' # no discount field in data
                    if discount_type != 'amount' or discount_type != 'percantage':
                        record['discount'] = u'0.00'
                        record['discount_type'] = u'amount'
                    else:
                        record['discount'] = discount
                        record['discount_type'] = discount_type

                    sale_price = product['price_sale']
                    if sale_price != None:
                        record['sale_price'] = sale_price
                    else:
                        record['sale_price'] = ''

                    retail_price = product['price']
                    if retail_price != None:
                        record['retail_price'] = retail_price
                    else:
                        record['retail_price'] = ''

                    shipping = product['price_shipping']
                    if shipping != None:
                        record['shipping_price'] = shipping

                    record['merchant_color'] = product['color']
                    merchant_color = product['color'].lower()
                    try:
                        allume_color = color_mapping[merchant_color]
                    except KeyError:
                        allume_color = u'other'
                    record['color'] = allume_color

                    record['gender'] = u'' # no data for gender?
                    record['style'] = product['style']

                    attribute_3_size = product['size']
                    attribute_3_size = attribute_3_size.upper()
                    attribute_3_size = attribute_3_size.replace('~', ',')
                    record['size'] = attribute_3_size

                    record['allume_size'] = product_feed_helpers.determine_allume_size(allume_category, attribute_3_size, size_mapping, shoe_size_mapping, size_term_mapping)

                    record['material'] = product['material']

                    attribute_8_age = product['age_range']
                    attribute_8_age.upper()
                    record['age'] = attribute_8_age

                    record['currency'] = product['currency']

                    availability = product['in_stock']
                    if availability == 'no':
                        availability = u'out-of-stock'
                    elif availability == '' or availability == 'yes':
                        availability = u'in-stock'
                    record['availability'] = availability

                    record['keywords'] = product['keywords']
                    record['primary_category'] = primary_category
                    record['secondary_category'] = secondary_category
                    # record['allume_category'] = u'allume_category' # allume_category hard coded
                    record['allume_category'] = allume_category # replace hard coding?
                    record['brand'] = product['manufacturer'] # doubles as brand
                    record['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S').decode('UTF-8')
                    record['merchant_name'] = merchant_name

                    # set defaults
                    record['is_best_seller'] = u'0'
                    record['is_trending'] = u'0'
                    record['allume_score'] = unicode(merchant_search_rank_mapping[long(merchant_id)])

                    # if there is a sale
                    try:
                        if float(sale_price) > 0:
                            record['current_price'] = sale_price
                        else:
                            record['current_price'] = retail_price
                    except (TypeError, ValueError):
                        record['current_price'] = retail_price

                    # is_deleted logic
                    if 'modification' == 'D': # hardcoded false?
                        record['is_deleted'] = u'1'
                    else:
                        record['is_deleted'] = u'0'

                    # size parsing and splitting, very likely a prime refactoring candidate
                    parent_attributes = copy(record)
                    sizes = product_feed_helpers.seperate_sizes(parent_attributes['size'])
                    product_id = parent_attributes['product_id']
                    if len(sizes) > 1:
                        for size in sizes:
                            child_record = copy(parent_attributes)
                            allume_size_arr = product_feed_helpers.parse_single_size(size, parent_attributes['product_name'], parent_attributes['allume_category'], known_text_sizes, known_number_sizes)
                            if len(allume_size_arr) > 1:
                                grandchild_record = copy(child_record)
                                child_record['size'] = size
                                for size in allume_size_arr:
                                    grandchild_record['size'] = size
                                    grandchild_record['allume_size'] = product_feed_helpers.parse_single_size(size, parent_attributes['product_name'], parent_attributes['allume_category'], known_text_sizes, known_number_sizes)[0]
                                    grandchild_record['product_id'] = product_feed_helpers.assign_product_id_size(product_id, grandchild_record['allume_size'])
                                    for key, value in grandchild_record.iteritems():
                                        grandchild_record[key] = product_feed_helpers.unicode_encode(value)
                                    writer.writerow(grandchild_record)
                                    writtenCount += 1
                                child_record['allume_size'] = u''
                                child_record['product_id'] = product_feed_helpers.assign_product_id_size(product_id, child_record['size'])
                                child_record['is_deleted'] = u'1'
                                for key, value in child_record.iteritems():
                                    child_record[key] = product_feed_helpers.unicode_encode(value)
                                writer.writerow(child_record)
                                writtenCount += 1
                            else:
                                child_record['size'] = size
                                child_record['allume_size'] = allume_size_arr[0]
                                child_record['product_id'] = product_feed_helpers.assign_product_id_size(product_id, child_record['allume_size'])
                                for key, value in child_record.iteritems():
                                    child_record[key] = product_feed_helpers.unicode_encode(value)
                                writer.writerow(child_record)
                                writtenCount += 1
                        parent_attributes['allume_size'] = u''
                        parent_attributes['is_deleted'] = u'1'
                        for key, value in parent_attributes.iteritems():
                            parent_attributes[key] = product_feed_helpers.unicode_encode(value)
                        writer.writerow(parent_attributes)
                        writtenCount += 1
                    else:
                        size = sizes[0]
                        allume_size_arr = product_feed_helpers.parse_single_size(size, parent_attributes['product_name'], parent_attributes['allume_category'], known_text_sizes, known_number_sizes)
                        if len(allume_size_arr) > 1:
                            child_record = copy(parent_attributes)
                            parent_attributes['size'] = size
                            for size in allume_size_arr:
                                child_record['size'] = size
                                child_record['allume_size'] = product_feed_helpers.parse_single_size(size, parent_attributes['product_name'], parent_attributes['allume_category'], known_text_sizes, known_number_sizes)[0]
                                child_record['product_id'] = product_feed_helpers.assign_product_id_size(product_id, child_record['allume_size'])
                                for key, value in child_record.iteritems():
                                    child_record[key] = product_feed_helpers.unicode_encode(value)
                                writer.writerow(child_record)
                                writtenCount += 1
                            parent_attributes['allume_size'] = u''
                            parent_attributes['is_deleted'] = u'1'
                            for key, value in parent_attributes.iteritems():
                                parent_attributes[key] = product_feed_helpers.unicode_encode(value)
                            writer.writerow(parent_attributes)
                            writtenCount += 1
                        else:
                            parent_attributes['size'] = size
                            parent_attributes['allume_size'] = allume_size_arr[0]
                            for key, value in parent_attributes.iteritems():
                                parent_attributes[key] = product_feed_helpers.unicode_encode(value)
                            writer.writerow(parent_attributes)
                            writtenCount += 1
                else:
                    categoriesSkipped += 1

    print('Processed %s records' % totalCount)
    print('Wrote %s records' % writtenCount)
    print('Discovered %s unmapped primary and secondary category pairs' % (CategoryMap.objects.count() - categoryCount))
    print('Dropped %s records due to gender' % genderSkipped)
    print('Dropped %s records due to inactive categories' % categoriesSkipped)
    # print('Added %s new merchants' % new_merchants)
    # new_merchants ?

    # call update_pepperjam here?
    # print('Updating non-upserted records')
    # product_feed_helpers.set_deleted_network_products('PepperJam')

def generate_product_id_pepperjam(SKU, merchant_id):
    """
    Takes in the product's SKU as unicode and merchant_id as unicode and generates
    a product_id as unicode to be used. Necessary because PepperJam data does not
    have any product_id information and a unique identifier is required to perform
    the upsert process for products.
    """
    # letter conversion dict that tries to minimize the length of digits added
    alpha_to_numeric = {
        u'a': u'1',
        u'b': u'2',
        u'c': u'3',
        u'd': u'4',
        u'e': u'5',
        u'f': u'6',
        u'g': u'7',
        u'h': u'8',
        u'i': u'9',
        u'j': u'10',
        u'k': u'11',
        u'l': u'12',
        u'm': u'13',
        u'n': u'14',
        u'o': u'15',
        u'p': u'16',
        u'q': u'17',
        u'r': u'18',
        u's': u'19',
        u't': u'20',
        u'u': u'21',
        u'v': u'22',
        u'w': u'23',
        u'x': u'24',
        u'y': u'25',
        u'z': u'26',
        # accomodate some additional characters seen in SKUs
        u'(': u'27',
        u')': u'28',
        u'.': u'29',
        u'-': u'30',
        u'/': u'31'
        }

    product_id = SKU + merchant_id
    product_id = product_id.lower()
    product_id = list(product_id)
    for i in range(0, len(product_id)):
        if product_id[i] in alpha_to_numeric.keys():
            product_id[i] = alpha_to_numeric[product_id[i]]
        # case when it is a character that is not in our keys, but it is also not alphanumeric
        elif not product_id[i].isalnum():
            product_id[i] = u'32'

    product_id = "".join(product_id)

    # handle when the prod_id is too big for django's big interger / mysql bigint(20)?
    product_id = product_id[:19]

    return product_id

# simple timeout and retry
def open_w_timeout_retry(url, tries, timeout, delay, backoff):
    """
    Attempts to open the provided URL within the specified timeout.
    Retries on error for tries amount of times, with a delay in seconds.
    Timeout is extended by multiplicative constant backoff until tries expire.
    """
    if tries > 0:
        try:
            return urllib2.urlopen(url, timeout = timeout)
        except urllib2.URLError as e:
            print(e)
            print("Retrying in %s seconds" % (delay))
            time.sleep(delay)
            print("Retrying!")
            return open_w_timeout_retry(url, tries - 1, timeout * backoff, delay, backoff)
    else:
        raise urllib2.URLError("URL causes significant problems, restart process")
 