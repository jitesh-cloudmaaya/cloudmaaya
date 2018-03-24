import os
import re
import csv
import yaml
from copy import copy
from . import mappings, product_feed_helpers
from product_api.models import Merchant, CategoryMap
from datetime import datetime, timedelta
from catalogue_service.settings import BASE_DIR

def cj(local_temp_dir, file_ending, cleaned_fields):
    # mappings
    merchant_mapping = mappings.create_merchant_mapping()
    color_mapping = mappings.create_color_mapping()
    category_mapping = mappings.create_category_mapping()
    allume_category_mapping = mappings.create_allume_category_mapping()
    size_mapping = mappings.create_size_mapping()
    shoe_size_mapping = mappings.create_shoe_size_mapping()
    size_term_mapping = mappings.create_size_term_mapping()

    network = mappings.get_network('CJ') # update this function to add the network

    destination = local_temp_dir + '/cleaned/cj_flat_file.csv'

    with open(destination, "w") as cleaned:
        file_list = []
        file_directory = os.listdir(local_temp_dir)

        pattern = re.compile(file_ending)
        for f in file_directory:
            if re.search(pattern, f):
                # file_list.append(os.path.join(os.getcwd(), local_temp_dir, f))
                file_list.append(f)

        # metric variables
        totalCount = 0
        writtenCount = 0
        genderSkipped = 0
        categoriesSkipped = 0
        merchantCount = Merchant.objects.count()
        categoryCount = CategoryMap.objects.count()

        csv.register_dialect('reading', delimiter='\t', quoting=csv.QUOTE_NONE, quotechar='')
        csv.register_dialect('writing', delimiter=',', quoting=csv.QUOTE_ALL, quotechar='"', doublequote=False, escapechar='\\', lineterminator='\n')

        cleaned_fieldnames = cleaned_fields.split(',')
        writer = csv.DictWriter(cleaned, cleaned_fieldnames, dialect = 'writing')

        for f in file_list:
            print f
            # might need to do some merchant name stuff here
            full_filepath = os.path.join(os.getcwd(), local_temp_dir, f)
            with open(full_filepath, "r") as data:
                lines = data.readlines()

                # merchant_is_active = mappings.is_merchant_active(merchant_id, merchant_name, network, merchant_mapping)
                # omit fieldnames arg to use headerlines
                reader = csv.DictReader(lines, restval = '', dialect = 'reading')
                # i = 0

                for datum in reader:
                    # totalCount += 1 # depening on how we want to count records skipped because of inactive merchants
                    # unicode
                    for key, value in datum.iteritems():
                        value = str(value) # check later, REVOLVE had an issue where a value was being read as [value] for some reason (as opposed to str)
                        datum[key] = value.decode('UTF-8')

                    # merchant name is the filename until the first dash (at least for all present examples)
                    pattern = re.compile('^[^-]*') # pattern matches until the first hyphen
                    match = re.search(pattern, f)
                    merchant_name = match.group(0) # match will be the entire filename in absence of a dash
                    merchant_name = merchant_name.lower() # make configuration file detection case agnostic
                    

                    config_path = BASE_DIR + '/tasks/product_feed_py/merchants_config_cj/'
                    fd = os.listdir(config_path)

                    default = 'default'
                    extension = '.yaml'
                    default_filename = default + extension
                    merchant_filename = merchant_name + extension

                    full_path = config_path + default_filename

                    if merchant_filename in fd:
                        full_path = config_path + merchant_filename

                    with open(full_path, "r") as config:
                        config_dict = yaml.load(config)
                        mapping_dict = config_dict['fields']

                    merchant_name_key = mapping_dict['merchant_name']
                    merchant_name = datum[merchant_name_key]
                    merchant_id = product_feed_helpers.generate_merchant_id(merchant_name)
                    # move activity check here
                    merchant_is_active = mappings.is_merchant_active(merchant_id, merchant_name, network, merchant_mapping)
                    if merchant_is_active:
                        # increment totalCount here??
                        totalCount += 1

                        # i += 1
                        # print '=========================================== BEGIN Product %s ===========================================' % i
                        # for key, value in datum.iteritems():
                        #     print (key, value)
                        # print '============================================ END Product %s ============================================' % i

                        # if i > 11:
                            # return

                        # faster way to perform the below?
                        # unpack the keys
                        merchant_color_key = mapping_dict['merchant_color']
                        size_key = mapping_dict['size']
                        keywords_key = mapping_dict['keywords']
                        currency_key = mapping_dict['currency']
                        SKU_key = mapping_dict['SKU']
                        product_name_key = mapping_dict['product_name']
                        availability_key = mapping_dict['availability']
                        product_image_url_key = mapping_dict['product_image_url']
                        product_url_key = mapping_dict['product_url']
                        buy_url_key = mapping_dict['buy_url']
                        retail_price_key = mapping_dict['retail_price']
                        sale_price_key = mapping_dict['sale_price']
                        long_product_description_key = mapping_dict['long_product_description']
                        primary_category_key = mapping_dict['primary_category']
                        shipping_price_key = mapping_dict['shipping_price']
                        manufacturer_name_key = mapping_dict['manufacturer_name']
                        secondary_category_key = mapping_dict['secondary_category']
                        short_product_description_key = mapping_dict['short_product_description']
                        manufacturer_part_number_key = mapping_dict['manufacturer_part_number']
                        product_type_key = mapping_dict['product_type']
                        discount_key = mapping_dict['discount']
                        discount_type_key = mapping_dict['discount_type']
                        gender_key = mapping_dict['gender']
                        style_key = mapping_dict['style']
                        material_key = mapping_dict['material']
                        age_key = mapping_dict['age']
                        brand_key = mapping_dict['brand']

                       # add a null mapping to each data point
                        datum['N/A'] = ''

                        gender = datum[gender_key]
                        gender = gender.upper()
                        gender = gender.replace('FEMALE', 'WOMEN')
                        gender = gender.replace('MALE', 'MEN')
                        gender = gender.replace('MAN', 'MEN')

                        skippedGenders = ['MEN', 'CHILD', 'KIDS', 'BOYS', 'GIRLS', 'BABY']
                        if gender in skippedGenders:
                            genderSkipped += 1
                            continue

                        primary_category = datum[primary_category_key]
                        secondary_category = datum[secondary_category_key]

                        allume_category = mappings.are_categories_active(primary_category, secondary_category, category_mapping, allume_category_mapping, merchant_name)
                        if allume_category:
                            record = {}

                            record['merchant_name'] = merchant_name

                            merchant_color = datum[merchant_color_key]
                            record['merchant_color'] = merchant_color
                            merchant_color = merchant_color.split(',')[0].lower()
                            try:
                                allume_color = color_mapping[merchant_color]
                            except:
                                allume_color = u'other'
                            record['color'] = allume_color

                            product_name = datum[product_name_key]
                            record['product_name'] = product_name

                            size = datum[size_key].upper()
                            size = size.replace('~', ',')
                            record['size'] = size
                            record['allume_size'] = product_feed_helpers.determine_allume_size(allume_category, size, size_mapping, shoe_size_mapping, size_term_mapping)

                            record['SKU'] = datum[SKU_key]

                            record['product_id'] = product_feed_helpers.generate_product_id(product_name, size, record['merchant_color'], record['SKU'])
                            record['merchant_id'] = merchant_id


                            record['product_image_url'] = datum[product_image_url_key]
                            record['buy_url'] = datum[buy_url_key]
                            record['product_url'] = datum[product_url_key]
                            try:
                                record['raw_product_url'] = product_feed_helpers.parse_raw_product_url(record['product_url'], 'url')
                            except KeyError as e:
                                print e
                                record['raw_product_url'] = u''

                            record['long_product_description'] = datum[long_product_description_key]
                            record['short_product_description'] = datum[short_product_description_key]
                            record['manufacturer_name'] = datum[manufacturer_name_key]
                            record['manufacturer_part_number'] = datum[manufacturer_part_number_key]
                            record['product_type'] = datum[product_type_key]

                            discount_type = datum[discount_type_key]
                            discount = datum[discount_key]
                            if discount_type != 'amount' or discount_type != 'percentage':
                                record['discount'] = u'0.00'
                                record['discount_type'] = u'amount'
                            else:
                                record['discount'] = discount
                                record['discount_type'] = discount_type

                            record['discount'] = datum[discount_key]
                            record['discount_type'] = datum[discount_type_key]

                            sale_price = datum[sale_price_key]
                            retail_price = datum[retail_price_key]
                            record['sale_price'] = sale_price
                            record['retail_price'] = retail_price

                            record['shipping_price'] = datum[shipping_price_key]
                            record['gender'] = gender
                            record['style'] = datum[style_key]
                            record['material'] = datum[material_key]
                            record['age'] = datum[age_key]
                            record['currency'] = datum[currency_key]

                            availability = datum[availability_key]
                            if availability == '':
                                availability = 'out-of-stock'
                            record['availability'] = availability

                            record['keywords'] = datum[keywords_key]
                            record['primary_category'] = primary_category
                            record['secondary_category'] = secondary_category
                            record['allume_category'] = allume_category
                            record['brand'] = datum[brand_key]
                            record['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                            try:
                                if float(sale_price) > 0:
                                    record['current_price'] = sale_price
                                else:
                                    record['current_price'] = retail_price
                            except ValueError:
                                record['current_price'] = retail_price

                            # defaults
                            record['is_best_seller'] = u'0'
                            record['is_trending'] = u'0'
                            record['allume_score'] = u'0'
                            record['is_deleted'] = u'0'

                            # finish unicode sandwich
                            for key, value in record.iteritems():
                                record[key] = value.encode('UTF-8')

                            # size splitting stuff
                            parent_attributes = copy(record)
                            sizes = product_feed_helpers.seperate_sizes(parent_attributes['size'])
                            product_id = parent_attributes['product_id']
                            if len(sizes) > 1: # the size attribute of the record was a comma seperated list
                                for size in sizes:
                                    parent_attributes['allume_size'] = product_feed_helpers.determine_allume_size(allume_category, size, size_mapping, shoe_size_mapping, size_term_mapping)
                                    # use the size mapping here also
                                    parent_attributes['size'] = size
                                    parent_attributes['product_id'] = product_feed_helpers.assign_product_id_size(product_id, size)
                                    writer.writerow(parent_attributes)
                                    writtenCount += 1
                                # set the parent record to is_deleted
                                record['is_deleted'] = 1

                            # write the record
                            writer.writerow(record)
                            writtenCount += 1
                        else:
                            categoriesSkipped += 1

    print('Processed %s records' % totalCount)
    print('Wrote %s records' % writtenCount)
    print('Discovered %s unmapped primary and secondary category pairs' % (CategoryMap.objects.count() - categoryCount))
    print('Discovered %s new merchant(s)' % (Merchant.objects.count() - merchantCount))
    print('Dropped %s records due to gender' % genderSkipped)
    print('Dropped %s records due to inactive categories' % categoriesSkipped)

    if 0: # remove this later
        print('Updating non-upserted Impact Radius products')
        product_feed_helpers.set_deleted_network_products('Impact Radius')

