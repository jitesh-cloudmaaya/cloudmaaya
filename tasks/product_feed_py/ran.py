import os
import datetime
import yaml
import urlparse
import csv
from django.db import connection
from . import mappings
from catalogue_service.settings import BASE_DIR

### attempt at writing record with logic
def clean_ran(local_temp_dir, file_ending):
    # instantiate relevant mappings
    merchant_mapping = mappings.create_merchant_mapping()
    color_mapping = mappings.create_color_mapping()
    category_mapping = mappings.create_category_mapping()
    allume_category_mapping = mappings.create_allume_category_mapping()

    destination = local_temp_dir + '/cleaned/flat_file.txt'
    with open(destination, "w") as cleaned:
        file_list = []
        file_directory = os.listdir(local_temp_dir)

        for f in file_directory:
            if f.endswith(file_ending):
                file_list.append(os.path.join(os.getcwd(), local_temp_dir, f))

        totalCount = 0
        writtenCount = 0

        genderSkipped = 0
        allumecategorySkipped = 0
        inactiveSkipped = 0

        # BEGIN CSV READER STUFF
        csv.register_dialect('pipes', delimiter='|', quoting=csv.QUOTE_NONE)
        for f in file_list:
            with open(f, "r") as csvfile:
                header = csvfile.readline()
                header = header.decode('utf-8')
                header = header.split('|')
                merchant_id = header[1]
                merchant_name = header[2]

                lines = csvfile.readlines()
                lines = lines[:-1]

                # handle if merchant_id not in merchant_table?
                try:
                    merchant_is_active = merchant_mapping[int(merchant_id)]
                except:
                    merchant_is_active = 0
                # check that the merchant_id is active in the merchant_mapping
                if merchant_is_active: # set the merchant_table active column to 1 for a few companies when testing
                    # check config files
                    config_path = BASE_DIR + '/tasks/product_feed_py/merchants_config/'
                    fd = os.listdir(config_path)

                    default = 'default'
                    extension = '.yaml'
                    default_filename = default + extension
                    merchant_id_filename = str(merchant_id) + extension

                    full_path = config_path + default_filename

                    if merchant_id_filename in fd:
                        # use that specific config file for reading the merchant file
                        # print 'specific file used!'
                        full_path = config_path + merchant_id_filename

                    with open(full_path, "r") as config:
                        # we shall use the default
                        config_dict = yaml.load(config)
                        fields = config_dict['fields'] # grabs the fields as an array
                    # print fields
                    reader = csv.DictReader(lines, fieldnames = fields, dialect = 'pipes')
                    for datum in reader:
                        totalCount += 1

                        # do we still need a unicode sandwich?

                        # for key, value in datum.iteritems():
                        #     print (key, value)

                        # do unicode sandwich stuff
                        for key, value in datum.iteritems():
                            datum[key] = value.decode('utf-8')

                        # breaking down the data from the merchant files
                        product_id = datum['product_id']
                        product_name = datum['product_name']
                        SKU = datum['SKU']
                        primary_category = datum['primary_category']
                        secondary_category = datum['secondary_category']
                        product_url = datum['product_url']

                        # implement a cheap fix for now, change when migrating to python's csv library
                        try:
                            raw_product_url = urlparse.parse_qs(urlparse.urlsplit(product_url).query)['murl'][0]
                            raw_product_url = raw_product_url.replace('|', '7%C') # look this over again when csv lib
                        except:
                            raw_product_url = '' # there was an error of some kind

                        product_image_url = datum['product_image_url']
                        buy_url = datum['buy_url']
                        short_product_description = datum['short_product_description']
                        long_product_description = datum['long_product_description']
                        discount = datum['discount']
                        if not discount:
                            discount = u'0.00' # unicode necessary or not
                        discount_type = datum['discount_type']
                        sale_price = datum['sale_price']
                        if not sale_price:
                            sale_price = u'0.00' # unicode necessary or not?
                        retail_price = datum['retail_price']
                        begin_date = datum['begin_date']
                        end_date = datum['end_date']
                        brand = datum['brand']
                        shipping = datum['shipping']
                        if not shipping:
                            shipping = u'0.00' # unicode necessary or not?
                        keywords = datum['keywords']
                        manufacturer_part_number = datum['manufacturer_part_number']
                        manufacturer_name = datum['manufacturer_name']
                        shipping_information = datum['shipping_information']
                        availability = datum['availability']
                        universal_product_code = datum['universal_product_code']
                        class_ID = datum['class_ID']
                        currency = datum['currency']
                        M1 = datum['M1']
                        pixel = datum['pixel']

                        # optional attributes begin here
                        # can have different orders
                        # modification must always be at the end (in deltas)
                        attribute_1_misc = datum['attribute_1_misc']
                        attribute_2_product_type = datum['attribute_2_product_type']
                        attribute_3_size = datum['attribute_3_size']
                        attribute_4_material = datum['attribute_4_material']
                        attribute_5_color = datum['attribute_5_color']
                        attribute_6_gender = datum['attribute_6_gender']
                        attribute_7_style = datum['attribute_7_style']
                        attribute_8_age = datum['attribute_8_age']
                        attribute_9 = datum['attribute_9']
                        attribute_10 = datum['attribute_10']

                        # in a delta file, there is 1 additional field for modification
                        if datum['modification']:
                            modification = datum['modification']
                        else: # not a delta file
                            modification = ''

                        # begins attribute manipulation logic

                        # moving gender check above categories check
                        # as all men categories have no entries in category tables
                        gender = attribute_6_gender.upper()
                        gender = gender.replace('FEMALE', 'WOMEN')
                        gender = gender.replace('MALE', 'MEN')
                        gender = gender.replace('MAN', 'MEN')

                        # check if gender makes record 'inactive'
                        if gender == 'MEN' or gender == 'CHILD' or gender == 'KIDS': # girls and boys?
                            genderSkipped += 1
                            continue


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
                            continue

                        # new logic for writing record
                        record = {}
                        record['product_id'] = product_id
                        record['merchant_id'] = merchant_id
                        record['product_name'] = product_name
                        record['long_product_description'] = long_product_description
                        record['short_product_description'] = short_product_description
                        record['product_url'] = product_url
                        record['raw_product_url'] = raw_product_url
                        record['product_image_url'] = product_image_url
                        record['buy_url'] = buy_url
                        record['manufacturer_name'] = manufacturer_name
                        record['manufacturer_part_number'] = manufacturer_part_number
                        record['SKU'] = SKU
                        record['product_type'] = attribute_2_product_type
                        if discount_type != 'amount' or discount_type != 'percentage':
                            record['discount'] = u'0.00'
                            record['discount_type'] = u'amount'
                        else:
                            record['discount'] = discount
                            record['discount_type'] = discount_type
                        record['sale_price'] = sale_price
                        record['retail_price'] = retail_price
                        record['shipping_price'] = shipping


                        # current behavior is take the first and find its mapping if possible
                        merchant_color = attribute_5_color.split(',')[0].lower()
                        record['merchant_color'] = merchant_color
                        try:
                            allume_color = color_mapping[merchant_color]
                        except:
                            allume_color = u'other'
                        record['color'] = allume_color

                        record['gender'] = gender
                        record['style'] = attribute_7_style

                        attribute_3_size = attribute_3_size.upper()
                        attribute_3_size = attribute_3_size.replace('~', ',')
                        record['size'] = attribute_3_size

                        record['material'] = attribute_4_material

                        attribute_8_age = attribute_8_age.upper()
                        record['age'] = attribute_8_age

                        record['currency'] = currency

                        if availability == '':
                            availability = 'out-of-stock'
                        record['availability'] = availability

                        record['keywords'] = keywords
                        # allume category information
                        record['primary_category'] = primary_category
                        record['secondary_category'] = secondary_category
                        record['allume_category'] = allume_category
                        record['brand'] = brand

                        record['updated_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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
                        if modification == 'D':
                            record['is_deleted'] = u'1'
                        else:
                            record['is_deleted'] = u'0'

                        # unicode sandwich finish
                        for key, value in record.iteritems():
                            record[key] = value.encode('utf-8')

                        print record

                        # reader = csv.DictReader(lines, fieldnames = fields, dialect = 'pipes')
                        # fieldnames = ?
                        fieldnames = ['product_id', 'merchant_id', 'product_name', 'long_product_description', 'short_product_description', 'product_url', 'raw_product_url', 'product_image_url', 'buy_url', 'manufacturer_name', 'manufacturer_part_number', 'SKU', 'product_type', 'discount', 'discount_type', 'sale_price', 'retail_price', 'shipping_price', 'color', 'merchant_color', 'gender', 'style', 'size', 'material', 'age', 'currency', 'availability', 'keywords', 'primary_category', 'secondary_category', 'allume_category', 'brand', 'updated_at', 'merchant_name', 'is_best_seller', 'is_trending', 'allume_score', 'current_price', 'is_deleted']
                        writer = csv.DictWriter(cleaned, fieldnames)
                        # write the reconstructed line to the cleaned file
                        writer.writerow(record)
                        writtenCount += 1
                        return

    print('Processed %s records' % totalCount)
    print('Wrote %s records' % writtenCount)
    print('Dropped %s records due to gender' % genderSkipped)
    print('Dropped %s records due to no allume_category_id mapping' % allumecategorySkipped)
    print('Dropped %s records due to inactive categories' % inactiveSkipped)



