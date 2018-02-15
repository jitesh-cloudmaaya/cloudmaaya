import os
import datetime
import yaml
import json
import urllib2
import urlparse
import csv
import time
from django.db import connection
from . import mappings
from . import product_feed_helpers
from catalogue_service.settings import BASE_DIR, PEPPERJAM_API_VERSION, PEPPERJAM_API_KEY
from product_api.models import CategoryMap, Network, Merchant, Product
from datetime import datetime, timedelta

# Set Up PepeprJam URL
PEPPER_JAM_API_BASE_URL = "https://api.pepperjamnetwork.com/%s/" % (PEPPERJAM_API_VERSION)

def get_merchants(status='joined'):

    # Set Up PepperJam URL
    pepper_jam_api_merchant_url = PEPPER_JAM_API_BASE_URL + "publisher/advertiser?apiKey=%s&status=%s&format=json" % (PEPPERJAM_API_KEY, status)

    # Look Up Existing DB Meta Data
    merchant_mapping = mappings.create_merchant_mapping()
    network = mappings.get_network('PepperJam')

    ## Dev Only
    # # Test Merchants Data
    # print("Getting local test data")
    # json_data = open('tasks/product_feed_py/sample_data/pepperjam_merchant.json')
    # merchants = json.load(json_data)
    # json_data.close()

    # Get Merchants
    ## Prod & Staging Only
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

def set_deleted_pepperjam_products(threshold = 12):
    """
    Helper method for use in the main get_data method. Collects a list of Pepperjam products
    that should have been upserted in the current run. For those that were not upserted, determined
    by a settable time threshold, set those products to a status of is_deleted = True.

    Args:
        threshold (int): The time threshold in hours. If the updated_at value of a record is threshold
        or more hours old, conclude it was not updated in the current upsert and set to deleted. 
    """
    # id of the pepperjam network for use in merchants' network_id
    pepperjam_id = Network.objects.get(name='PepperJam').id
    # get the pepperjam merchants that were active (and hence were just updated)
    merchants = Merchant.objects.filter(active=True, network_id = pepperjam_id) # multiple arguments over chaining for performance
    merchant_ids = merchants.values_list('external_merchant_id')
    # get the products of these merchants
    products = Product.objects.filter(merchant_id__in = merchant_ids) # up to here is confirmed what we want
    datetime_threshold = datetime.now() - timedelta(hours = threshold) # comparison threshold is 12 hours ago or more
    deleted_products = products.filter(updated_at__lte = datetime_threshold)
    # set is deleted for all of them and save in bulk (WILL NOT perform Product save callbacks)
    deleted_products.update(is_deleted = True)

def get_data(local_temp_dir, cleaned_fieldnames):

     # Set Up PepperJam URL
    pepper_jam_api_product_url = PEPPER_JAM_API_BASE_URL + "publisher/creative/product?apiKey=%s&format=json" % (PEPPERJAM_API_KEY)
    #pepper_jam_api_product_url = "https://api.pepperjamnetwork.com/20120402/publisher/creative/product?apiKey=48db78a072444a019989822d21aa513a5f0f67bb2363d6370b9e59b23bd4b29d&format=json&page=26"

    # Get Mapping Data
    merchant_mapping = get_merchants(status='joined') # new way to create merchant_mapping?
    color_mapping = mappings.create_color_mapping()
    category_mapping = mappings.create_category_mapping()
    allume_category_mapping = mappings.create_allume_category_mapping()
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
            # print("Getting Data")
            # print(pepper_jam_api_product_url)
            # json_data = open('tasks/product_feed_py/sample_data/pepperjam_product.json')
            # product_feed = json.load(json_data)
            # json_data.close()

            # commenting out because API only has X amount of access allowed in a day
            ## Prod & Staging Only
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
                except:
                    print 'somehow used a merchant_id now present in the mapping'
                    continue
                # check that the merchant_id is active in the merchant mapping
                if merchant_is_active == False:
                    continue

                primary_category = product['category_program']
                secondary_category = product['category_network']
                allume_category = mappings.are_categories_active(primary_category, secondary_category, category_mapping, allume_category_mapping, merchant_name)
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
                    except Exception as e:
                        print e
                        record['raw_product_url'] = u''
                    # record['raw_product_url'] = urlparse.parse_qs(urlparse.urlsplit(buy_url).query)['url'][0]
                    record['product_image_url'] = product['image_url']
                    record['buy_url'] = buy_url
                    record['manufacturer_name'] = product['manufacturer']
                    record['manufacturer_part_number'] = product['mpn']
                    record['SKU'] = product['sku']

                    product_id = generate_product_id(product['sku'], merchant_id)
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

                    merchant_color = product['color']
                    record['merchant_color'] = merchant_color
                    try:
                        allume_color = color_mapping[merchant_color]
                    except:
                        allume_color = u'other'
                    record['color'] = allume_color

                    record['gender'] = u'' # no data for gender?
                    record['style'] = product['style']

                    attribute_3_size = product['size']
                    attribute_3_size = attribute_3_size.upper()
                    attribute_3_size = attribute_3_size.replace('~', ',')
                    record['size'] = attribute_3_size

                    record['material'] = product['material']

                    attribute_8_age = product['age_range']
                    attribute_8_age.upper()
                    record['age'] = attribute_8_age

                    record['currency'] = product['currency']

                    if product['in_stock'] == '':
                        availability = 'out-of-stock'
                    else:
                        availability = product['in_stock']
                    record['availability'] = availability

                    record['keywords'] = product['keywords']
                    record['primary_category'] = primary_category
                    record['secondary_category'] = secondary_category
                    # record['allume_category'] = u'allume_category' # allume_category hard coded
                    record['allume_category'] = allume_category # replace hard coding?
                    record['brand'] = product['manufacturer'] # doubles as brand
                    record['updated_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S').decode('UTF-8')
                    record['merchant_name'] = merchant_name

                    # set defaults
                    record['is_best_seller'] = u'0'
                    record['is_trending'] = u'0'
                    record['allume_score'] = u'0'

                    # if there is a sale
                    try:
                        if float(sale_price) > 0:
                            record['current_price'] = sale_price
                        else:
                            record['current_price'] = retail_price
                    except:
                        record['current_price'] = retail_price

                    # is_deleted logic
                    if 'modification' == 'D': # hardcoded false?
                        record['is_deleted'] = u'1'
                    else:
                        record['is_deleted'] = u'0'

                    # end unicode sandwich
                    for key, value in record.iteritems():
                        record[key] = value.encode('UTF-8')

                    # check size here to see if we should write additional 'child' records?
                    parent_attributes = copy(record)
                    sizes = product_feed_helpers.seperate_sizes(parent_attributes['size'])
                    product_id = parent_attributes['product_id']
                    if len(sizes) > 1: # the size attribute of the record was a comma seperated list
                        for size in sizes:
                            parent_attributes['product_id'] = product_feed_helpers.assign_product_id_size(product_id, size)
                            parent_attributes['size'] = size
                            writer.writerow(parent_attributes)
                            writtenCount += 1
                        # set the parent record to is_deleted
                        record['is_deleted'] = 1

                    # write the reconstructed line to the cleaned file using the csvwriter
                    writer.writerow(record)
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
    print('Updating non-upserted records')
    set_deleted_pepperjam_products()

def generate_product_id(SKU, merchant_id):
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

"""

    product_id: 0
    product_name: 1
    SKU: 2
    primary_category: 3
    secondary_category: 4
    product_url: 5
    product_image_url: 6
    buy_url: 7
    short_product_description: 8
    long_product_description: 9
    discount: 10
    discount_type: 11
    sale_price: 12
    retail_price: 13
    begin_date: 14
    end_date: 15
    brand: 16
    shipping: 17
    keywords: 18
    manufacturer_part_number: 19
    manufacturer_name: 20
    shipping_information: 21
    availability: 22
    universal_product_code: 23
    class_ID: 24
    currency: 25
    M1: 26
    pixel: 27
    attribute_1_misc: 28
    attribute_2_product_type: 29
    attribute_3_size: 30
    attribute_4_material: 31
    attribute_5_color: 32
    attribute_6_gender: 33
    attribute_7_style: 34
    attribute_8_age: 35
    attribute_9: 36
    attribute_10: 37
    modification: 38


"""
#SAMPLE API RESPONSE
"""
{
"meta" : {
    "status" : {     
        "code" : 200,
        "message" : "OK"
    },
    "pagination" : {     
        "total_results" : 1000,
        "total_pages" : 2,
        "next" : {  // Only available if there's a next page
            "rel" : "next",
            "href" : "<next_page_link>",
            "description" : "Next Page"
        },
        "previous" : {  // Only available if there's a previous page 
            "rel" : "previous",
            "href" : "<previous_page_link>",
            "description" : "Previous Page"
        }
    },
    "requests" : {     
        "current" : <current_requests>,
        "maximum" : <maximum_requests_per_day>
    },
},
"data" : { ... } // Can be an array [] or and object {}
}
"""

##### PRODUCT SERVICE DETAILS

"""

The product creative resource allows a publisher to pull product creatives for the advertisers they're working with.

GET
Request Parameters
Parameter	Description	Possible Values	Default	Required?
programIds	A comma-separated list of program ids to filter by.	* 123,456,789	N/A	No
categories	A comma-separated list of category ids to filter by.
Use the category resource to retrieve these ids.	* 123,456,789	N/A	No
keywords	A space-separated list of search terms to filter by.	* keyword1 keyword2 keyword3	N/A	No


Response Fields
Field	Description	Notes
age_range	Suggested age range	10-14
artist	Media artist	The Beatles
aspect_ratio	Screen aspect ratio	16:9
author	Media author	John Steinbeck
battery_life	Battery life	3
binding	Book binding	hardcover
buy_url	Destination URL	http://site.com/product
category_network	eBay Enterprise Affiliate Network specific category (sub categories optionally delimited by '>')	apparel > pants
category_program	Merchant specific category (sub categories optionally delimited by '>')	apparel > pants
color	Color of item	green
color_output	Whether output is color or not	yes
condition	Condition	new
description_long	Long description	Computing device that makes direct use of quantum merchanical phenomena. The fundamental building block of this computer is the qubit.
description_short	Short description	Computing device that makes direct use of quantum merchanical phenomena.
director	Movie director	Steven Spielberg
discontinued	Whether product is discontinued or not	yes
display_type	Display type	LCD
edition	Media edition	collectors
expiration_date	Expiration date	2009-04-04
features	Special features	machine washable
focus_type	Focus type	manual
format	Format	DVD
functions	Functions	photo capability
genre	Genere	Rock and Roll
heel_height	Heel height	1.5 inches
height	Height	28 inches
image_thumb_url	Thumbnail image URL	http://site.com/thumb/image.jpg
image_url	Standard image URL	http://site.com/image.jpg
installation	Installation type	free standing
in_stock	Whether product is in stock or not	yes
isbn	Book ISBN	0123456789
keywords	Space separated list of keywords	quantum qubit computing
length	Length	3 feet
load_type	Load type	top
location	Shipping location	Dallas, TX
made_in	Manufacturing country	USA
manufacturer	Manufacturer or brand	Sony
material	Contstruction material	graphite
megapixels	Megapixels	7.2
memory_capacity	Memory capacity	8 gigabytes
memory_card_slot	Memory card slot type	bluetooth
memory_type	Memory type	flash
model_number	Model number	442244
mpn	Manufacturer part number	HMC4415AA
name	Name or title	cutlery set
occasion	Recommended usage occasion	Thanksgiving
operating_system	Operating system	Linux
optical_drive	Optical drive type	CD-RW
pages	Number of pages	425
payment_accepted	Accepted payment methods	cash/check
payment_notes	Additional payment notes	POD
platform	Platform	Nintendo Wii
price	Selling price	15.00
price_retail	Manufacturer suggested retail price	17.50
price_sale	Discount price	12.50
price_shipping	Shipping price	2.50
processor	Processor type	Intel
publisher	Publisher	Pinacle Publishing
quantity_in_stock	Number of items in stock	144
rating	Rating	G
recommended_usage	Recommended usage	home
resolution	Screen resolution	1080p
screen_size	Screen size	52 inches
shipping_method	Shipping methods	ground
shoe_size	Shoe size	12
shoe_width	Shoe Width	wide
size	Size	large
sku	Stock keeping unit	45588977
staring	Staring actors	Big Bird
style	Style	formal
tech_spec_url	Technical Specifications URL	http://site.com/specs/product
tracks	Total number of tracks	12
upc	Universal product code	434724479304
weight	Weight	10 pounds
width	Width	2 feet
wireless_interface	Wireless interface	bluetooth
year	Year of manufacture - YYYY	2001
zoom	Maxium zoom	3x


"""