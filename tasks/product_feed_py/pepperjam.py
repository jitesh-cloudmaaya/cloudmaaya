import os
import datetime
import yaml
import json
import urllib2
import urlparse
import csv
from django.db import connection
from . import mappings
from catalogue_service.settings import BASE_DIR, PEPPERJAM_API_VERSION, PEPPERJAM_API_KEY

# Set Up PepeprJam URL
PEPPER_JAM_API_BASE_URL = "https://api.pepperjamnetwork.com/%s/" % (PEPPERJAM_API_VERSION)

def get_merchants(status='joined'):


    # Set Up PepperJam URL
    pepper_jam_api_merchant_url = PEPPER_JAM_API_BASE_URL + "publisher/advertiser?apiKey=%s&status=%s&format=json" % (PEPPERJAM_API_KEY, status)

    # Look Up Existing DB Meta Data
    merchant_mapping = mappings.create_merchant_mapping()
    network = mappings.get_network('PepperJam')

    ## Dev Only
    # Test Merchants Data
    print("Getting local test data")
    json_data = open('tasks/product_feed_py/sample_data/pepperjam_merchant.json')

    # Get Merchants
    # merchants = json.load(urllib2.urlopen(pepper_jam_api_merchant_url))
    
    # Create some variables to count process metrics
    new_merchants = 0

    for merchant in merchants['data']:
        merchant_id = long(merchant['id'])
        merchant_name = merchant['name']

        try:
            merchant_is_active = merchant_mapping[merchant_id]
        except:
            mappings.add_new_merchant(merchant_id, merchant_name, network, False)
            merchant_mapping = mappings.create_merchant_mapping() #Reload Merchant Mapping
            new_merchants += 1

    print('Added %s new merchants' % new_merchants)


def discover_categories():
    pass

def get_data(local_temp_dir):

     # Set Up PepperJam URL
    pepper_jam_api_product_url = PEPPER_JAM_API_BASE_URL + "publisher/creative/product?apiKey=%s&format=json" % (PEPPERJAM_API_KEY)
    #pepper_jam_api_product_url = "https://api.pepperjamnetwork.com/20120402/publisher/creative/product?apiKey=48db78a072444a019989822d21aa513a5f0f67bb2363d6370b9e59b23bd4b29d&format=json&page=26"


    # Get Mapping Data
    merchant_mapping = mappings.create_merchant_mapping()
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
    allumecategorySkipped = 0
    inactiveSkipped = 0
    new_merchants = 0

    with open(destination, "w") as cleaned:
        # first guess at dialect
        csv.register_dialect('writing', delimiter=',', quoting=csv.QUOTE_ALL, quotechar='"', doublequote=False, escapechar='\\')
        # cleaned_fieldnames const until can pass in yaml
        cleaned_fieldnames = ['product_id', 'merchant_id', 'product_name', 'long_product_description', 'short_product_description', 'product_url', 'raw_product_url', 'product_image_url', 'buy_url', 'manufacturer_name', 'manufacturer_part_number', 'SKU', 'product_type', 'discount', 'discount_type', 'sale_price', 'retail_price', 'shipping_price', 'color', 'merchant_color', 'gender', 'style', 'size', 'material', 'age', 'currency', 'availability', 'keywords', 'primary_category', 'secondary_category', 'allume_category', 'brand', 'updated_at', 'merchant_name', 'is_best_seller', 'is_trending', 'allume_score', 'current_price', 'is_deleted']
        # intiialize the csv wrtier
        writer = csv.DictWriter(cleaned, cleaned_fieldnames, dialect = 'writing')

        more_pages = True

        while more_pages:

            # commenting out because API only has X amount of access allowed in a day
            ## Prod & Staging Only
            # print("Getting Data")
            # print(pepper_jam_api_product_url)
            # product_feed = json.load(urllib2.urlopen(pepper_jam_api_product_url))

            ## Dev Only
            # print("Getting Data")
            # print(pepper_jam_api_product_url)
            json_data = open('tasks/product_feed_py/sample_data/pepperjam_product.json')  
            product_feed = json.load(json_data)
            json_data.close()

            if 'next' in product_feed['meta']['pagination']:
                pepper_jam_api_product_url = product_feed['meta']['pagination']['next']['href']
            else:
                more_pages = False

            for product in product_feed['data']:

                merchant_id = product['program_id']
                merchant_name = product['program_name']

                # Test if Mechant Is Active
                try:
                    merchant_is_active = merchant_mapping[int(merchant_id)]
                except:
                    mappings.add_new_merchant(merchant_id, merchant_name, network, False)
                    merchant_mapping = mappings.create_merchant_mapping() #Reload Merchant Mapping
                    new_merchants += 1
                    merchant_is_active = 0
                # check that the merchant_id is active in the merchant mapping
                if merchant_is_active == False:
                    continue

                primary_category = product['category_program']
                secondary_category = product['category_network']

                # temporarily don't skip if product is of an inactive category

                ################### DON"T SKIP ANY RECORDS FOR NOW ################ 

                # Test if Category is Active
                # try:
                #     identifier = (primary_category, secondary_category)
                #     allume_category_id, active = category_mapping[identifier]
                #     # activity check on the primary, secondary category pair
                #     if not active:
                #         # inactiveSkipped += 1
                #         # continue
                #         pass
                #     # print(active)
                #     allume_category, active = allume_category_mapping[allume_category_id]
                #     # activity check on the allume_category
                #     if not active:
                #         # inactiveSkipped += 1
                #         # continue
                #         pass
                # except:
                #     # there is no entry in the category tables for the provided categories
                #     # assume inactive?
                #     allumecategorySkipped += 1
                #     mappings.add_category_map(primary_category, secondary_category, None, False, True)
                #     allume_category_mapping = mappings.create_allume_category_mapping()
                #     category_mapping = mappings.create_category_mapping()
                #     continue

                record = {}
                record['product_id'] = u'-99'
                record['merchant_id'] = merchant_id
                record['product_name'] = product['name'] # product_name
                record['long_product_description'] = product['description_long']
                record['short_product_description'] = product['description_short']
                buy_url = product['buy_url']
                record['product_url'] = buy_url # product_url == buy_url?
                record['raw_product_url'] = urlparse.parse_qs(urlparse.urlsplit(buy_url).query)['url'][0]
                record['product_image_url'] = product['image_url']
                record['buy_url'] = buy_url
                record['manufacturer_name'] = product['manufacturer']
                record['manufacturer_part_number'] = product['mpn']
                record['SKU'] = product['sku']
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
                record['allume_category'] = u'allume_category' # allume_category hard coded
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
                    record['current_price']

                # is_deleted logic
                if 'modification' == 'D': # hardcoded false?
                    record['is_deleted'] = u'1'
                else:
                    record['is_deleted'] = u'0'

                # end unicode sandwich
                for key, value in record.iteritems():
                    record[key] = value.encode('UTF-8')

                # write the reconstructed line to the cleaned file using the csvwriter
                writer.writerow(record)
                writtenCount += 1

    print('Processed %s records' % totalCount)
    print('Wrote %s records' % writtenCount)
    print('Dropped %s records due to gender' % genderSkipped)
    print('Dropped %s records due to no allume_category_id mapping' % allumecategorySkipped)
    print('Dropped %s records due to inactive categories' % inactiveSkipped)
    print('Added %s new merchants' % new_merchants)
    # new_merchants ?
		

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