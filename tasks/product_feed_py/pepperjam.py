import os
import datetime
import yaml
import json
import urllib2
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

    # Get Merchants
    merchants = json.load(urllib2.urlopen(pepper_jam_api_merchant_url))
    
    # Create some variables to count process metrics
    new_merchants = 0

    for merchant in merchants['data']:
        merchant_id = int(merchant['id'])
        merchant_name = merchant['name']

        try:
            merchant_is_active = merchant_mapping[merchant_id]
        except:
            mappings.add_new_merchant(merchant_id, merchant_name, network, False)
            merchant_mapping = mappings.create_merchant_mapping() #Reload Merchant Mapping
            new_merchants += 1

    print('Added %s new merchants' % new_merchants)

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
    destination = local_temp_dir + '/ppj_flat_file.txt'

    # Create some variables to count process metrics
    totalCount = 0
    writtenCount = 0
    genderSkipped = 0
    allumecategorySkipped = 0
    inactiveSkipped = 0
    new_merchants = 0


    with open(destination, "w") as cleaned:

        more_pages = True

        while more_pages:

            ## Prod & Staging Only
            print("Getting Data")
            print(pepper_jam_api_product_url)
            product_feed = json.load(urllib2.urlopen(pepper_jam_api_product_url))

            ## Dev Only
            #json_data = open('tasks/product_feed_py/sample_data/pepperjam_product.json')  
            #product_feed = json.load(json_data)
            #json_data.close()

            if 'next' in  product_feed['meta']['pagination']:
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

                # Test if Category is Active
                try:
                    identifier = (primary_category, secondary_category)
                    allume_category_id, active = category_mapping[identifier]
                    # activity check on the primary, secondary category pair
                    if not active:
                        inactiveSkipped += 1
                        continue
                    # print(active)
                    allume_category, active = allume_category_mapping[allume_category_id]
                    # activity check on the allume_category
                    if not active:
                        inactiveSkipped += 1
                        continue
                except:
                    # there is no entry in the category tables for the provided categories
                    # assume inactive?
                    allumecategorySkipped += 1
                    mappings.add_category_map(primary_category, secondary_category, None, False, True)
                    allume_category_mapping = mappings.create_allume_category_mapping()
                    category_mapping = mappings.create_category_mapping()
                    continue

                ## Build Record for Insertion
                record = ''
                record += "-99" + u'|' #product_id
                record += merchant_id + u'|'
                record += product['name'] + u'|' #product_name
                record += product['description_long'] + u'|' #long_product_description
                record += product['description_short'] + u'|' #short_product_description
                record += product['buy_url'] + u'|' #product_url
                record += product['image_url'] + u'|' #product_image_url
                record += product['buy_url'] + u'|' #buy_url
                record += product['manufacturer'] + u'|' #manufacturer_name
                record += product['mpn'] + u'|' #manufacturer_part_number
                record += product['sku'] + u'|' #SKU
                record += 'attribute_2_product_type' + u'|' #


                discount_type = "" #No Discount Field in the Data
                if discount_type != "amount" or discount_type != "percentage":
                    record += '0.0|' # how to indicate null or 0 as in sql?
                    record += 'amount|'
                else:
                    record += discount + u'|'
                    record += discount_type + u'|'

                sale_price = product['price_sale'] #float(product['price_sale'].decode('utf-8'))
                if sale_price != None:
                    record += sale_price + u'|' #retail_price
                else:
                    record += "" + u'|' #retail_price

                retail_price = product['price'] #float(product['price_retail'].decode('utf-8'))
                if retail_price != None:
                    record += retail_price + u'|' #retail_price
                else:
                    record += "" + u'|' #retail_price

                shipping = product['price_shipping'] #float(product['price_shipping'].decode('utf-8'))
                if shipping != None:
                    record += shipping + u'|' #shipping
                else:
                    record += "" + u'|' #shipping

                # current behavior is take the first and find its mapping if possible
                color = product['color']
                try:
                    record += color_mapping[color] + u'|'
                except: # where there is no analog
                    record += "other|"

                record += product['color'] + u'|' # attribute_5_color merchant color field

                # gender
                record += "" + u'|' #gender
                record += product['style'] + u'|' #attribute_7_style

                attribute_3_size = product['size']
                attribute_3_size = attribute_3_size.upper()
                attribute_3_size = attribute_3_size.replace('~', ',')
                record += attribute_3_size + u'|'

                record +=  product['material'] + u'|' #attribute_4_material

                attribute_8_age = product['age_range']
                record += attribute_8_age + u'|'

                record += product['currency'] + u'|' #currency

                if product['in_stock'] == '':
                    availability = 'out-of-stock'
                else:
                    availability = product['in_stock']
                record += availability + u'|'


                record += product['keywords'] + u'|' #keywords

                # allume category information
                record += primary_category + u'|'
                record += secondary_category + u'|'

                record += 'allume_category' + u'|' #allume_category

                record += product['manufacturer'] + u'|' #brand
                # double check date formatting
                record += datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + u'|'
                # record += datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f') + ',') ?
                # end date
                record += merchant_name + u'|'
                # how to indicate null or 0 as in ran.sql
                record += '0|' # is_best_seller default
                record += '0|' # is_trending default
                record += '0|' # allume_score default

                sale_price = product['price_sale']
                try:
                    # if there is a sale
                    if float(sale_price) > 0: # OR NOT NULL ??
                        record += sale_price + u'|'
                    else:
                        record += retail_price + u'|'
                except:
                    record += retail_price + u'|'

                # is_deleted logic
                if "modification" == 'D':
                    record += '1\n' # is this okay given is_deleted is boolean data type
                else:
                    record += '0\n'

                cleaned.write(record.encode('UTF-8'))
                writtenCount += 1

    print('Processed %s records' % totalCount)
    print('Wrote %s records' % writtenCount)
    print('Dropped %s records due to gender' % genderSkipped)
    print('Dropped %s records due to no allume_category_id mapping' % allumecategorySkipped)
    print('Dropped %s records due to inactive categories' % inactiveSkipped)
    print('Added %s new merchants' % new_merchants)
    new_merchants
		

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