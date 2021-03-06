import os
import yaml
import urlparse
import csv
import re
from copy import copy
from django.db import connection
from tasks.product_feed_py import mappings, product_feed_helpers
from catalogue_service.settings import BASE_DIR
from product_api.models import Merchant, CategoryMap, Network, Product, SynonymCategoryMap, ExclusionTerm
from datetime import datetime, timedelta

### attempt at writing record with logic
def clean_ran(local_temp_dir, file_ending, cleaned_fields, is_delta=False):
    # instantiate relevant mappings
    merchant_mapping = mappings.create_merchant_mapping()
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

    # initialize network instance for adding potential new merchants
    network = mappings.get_network('RAN')

    destination = local_temp_dir + '/cleaned/flat_file.csv'

    with open(destination, "w") as cleaned:
        file_list = []
        file_directory = os.listdir(local_temp_dir)

        for f in file_directory:
            if f.endswith(file_ending):
                file_list.append(os.path.join(os.getcwd(), local_temp_dir, f))

        # metric variables
        totalCount = 0
        writtenCount = 0
        genderSkipped = 0
        categoriesSkipped = 0
        merchantCount = Merchant.objects.count()
        categoryCount = CategoryMap.objects.count()

        # different dialects for reading and writing
        csv.register_dialect('reading', delimiter='|', quoting=csv.QUOTE_NONE, quotechar='')
        csv.register_dialect('writing', delimiter=',', quoting=csv.QUOTE_ALL, quotechar='"', doublequote=False, escapechar='\\', lineterminator='\n')

        cleaned_fieldnames = cleaned_fields.split(',')
        writer = csv.DictWriter(cleaned, cleaned_fieldnames, dialect = 'writing')
        for f in file_list:
            with open(f, "r") as csvfile:
                header = csvfile.readline()
                header = header.decode('UTF-8')
                header = header.split('|')
                merchant_id = header[1]
                merchant_name = header[2]

                lines = csvfile.readlines()
                lines = lines[:-1]

                merchant_is_active = mappings.is_merchant_active(merchant_id, merchant_name, network, merchant_mapping)
                if merchant_is_active: # set the merchant_table active column to 1 for a few companies when testing
                    # check config files
                    config_path = BASE_DIR + '/tasks/product_feed_py/merchants_config/ran/'
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

                        try: # not all merchants will have this field
                            # the above will now be a dictionary like {'primary_category': ['primary_category', 'product_type']}
                            tiered_assignments = config_dict['tiered_assignment_fields']
                        except KeyError:
                            tiered_assignments = {}

                    # print fields
                    reader = csv.DictReader(lines, fieldnames = fields, restval='', dialect = 'reading')
                    for datum in reader:
                        totalCount += 1

                        # do unicode sandwich stuff
                        for key, value in datum.iteritems():
                            datum[key] = value.decode('UTF-8')

                        # breaking down the data from the merchant files
                        product_id = datum['product_id']
                        product_name = datum['product_name']
                        SKU = datum['SKU']
                        primary_category = product_feed_helpers.product_field_tiered_assignment(tiered_assignments, 'primary_category', datum, datum['primary_category'])
                        secondary_category = product_feed_helpers.product_field_tiered_assignment(tiered_assignments, 'secondary_category', datum, datum['secondary_category'], synonym_category_mapping = synonym_category_mapping, synonym_other_category_mapping = synonym_other_category_mapping, exclusion_terms = exclusion_terms)
                        product_url = datum['product_url']

                        try:
                            raw_product_url = product_feed_helpers.parse_raw_product_url(product_url, 'murl')
                            # raw_product_url = urlparse.parse_qs(urlparse.urlsplit(product_url).query)['murl'][0]
                        except KeyError as e:
                            print e
                            raw_product_url = u'' # there was an error of some kind

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
                        modification = datum['modification']

                        # moving gender check above categories check
                        # as all men categories have no entries in category tables
                        gender = attribute_6_gender.upper()
                        gender = gender.replace('FEMALE', 'WOMEN')
                        gender = gender.replace('MALE', 'MEN')
                        gender = gender.replace('MAN', 'MEN')

                        # check if gender makes record 'inactive'
                        skippedGenders = ['MEN', 'CHILD', 'KIDS', 'BOYS', 'GIRLS', 'BABY']
                        if gender in skippedGenders:
                            genderSkipped += 1
                            continue

                        allume_category = mappings.are_categories_active(primary_category, secondary_category, category_mapping, allume_category_mapping, merchant_name, exclusion_terms, synonym_other_terms, synonym_terms)
                        if allume_category:
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
                            record['merchant_color'] = attribute_5_color
                            merchant_color = attribute_5_color.split(',')[0].lower()
                            try:
                                allume_color = color_mapping[merchant_color]
                            except KeyError:
                                allume_color = u'other'
                            record['color'] = allume_color

                            record['gender'] = gender
                            record['style'] = attribute_7_style

                            attribute_3_size = attribute_3_size.upper()
                            attribute_3_size = attribute_3_size.replace('~', ',')
                            record['size'] = attribute_3_size


                            # record['allume_size'] = product_feed_helpers.determine_allume_size(allume_category, attribute_3_size, size_mapping, shoe_size_mapping, size_term_mapping)

                            record['material'] = attribute_4_material

                            attribute_8_age = attribute_8_age.upper()
                            record['age'] = attribute_8_age

                            record['currency'] = currency

                            if availability == '' or availability == 'no':
                                availability = u'out-of-stock'
                            elif availability == 'yes':
                                availability = u'in-stock'
                            record['availability'] = availability

                            record['keywords'] = keywords
                            # allume category information
                            record['primary_category'] = primary_category
                            record['secondary_category'] = secondary_category
                            record['allume_category'] = allume_category
                            record['brand'] = brand

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
                            if modification == 'D':
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
    print('Discovered %s new merchant(s)' % (Merchant.objects.count() - merchantCount))
    print('Dropped %s records due to gender' % genderSkipped)
    print('Dropped %s records due to inactive categories' % categoriesSkipped)

    # test the theory
    # UPDATE: Csn't use on the Delta File as it will not include records that didn't change but are still live
    # if not is_delta:
    #     print('Setting deleted for non-upserted products')
    #     product_feed_helpers.set_deleted_network_products('RAN')
