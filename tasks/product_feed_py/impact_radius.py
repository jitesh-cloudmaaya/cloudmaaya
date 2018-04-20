import os
import yaml
import urlparse
import re
import csv
from tasks.product_feed_py import mappings, product_feed_helpers
from copy import copy
from catalogue_service.settings import BASE_DIR
from product_api.models import Merchant, CategoryMap, Network, Product, SynonymCategoryMap, ExclusionTerm
from itertools import izip
from datetime import datetime, timedelta

def impact_radius(local_temp_dir, file_ending, cleaned_fields):
    # mappings
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

    # for use when adding a mapping
    exclusion_terms = mappings.create_exclusion_term_mapping()
    synonym_other_terms = SynonymCategoryMap.objects.filter(category = 'Other').values_list('synonym', flat=True)
    synonym_terms = SynonymCategoryMap.objects.values_list('category', flat=True)

    # initialize network instance for adding potential new merchants
    network = mappings.get_network('Impact Radius') # name subject to change?

    destination = local_temp_dir + '/cleaned/ir_flat_file.csv'

    with open(destination, "w") as cleaned:
        file_list = []
        file_directory = os.listdir(local_temp_dir)

        for f in file_directory:
            if f.endswith(file_ending):
                file_list.append(f)
                # file_list.append(os.path.join(os.getcwd(), local_temp_dir, f))

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

        merchant_names = set()
        pattern = '^[^-]+' # read until the first hyphen
        for f in file_list:
            try:
                merchant_name = re.match(pattern, f).group(0)
            except AttributeError, IndexError:
                # .txt file would not be of the format we expect from ir ftp server
                continue
            merchant_names.add(merchant_name) # double check function name

        merchant_file_pairs = [] # list of file pair tuples
        for merchant_name in merchant_names:
            # double check these patterns
            pattern2 = '^' + merchant_name + '.*_IR.txt$' # ?

            for f in file_list:
                try:
                    file_of_interest1 = re.match(pattern2, f).group(0)
                except AttributeError:
                    continue # i think?

            pattern3 = '^' + merchant_name + '.*_GOOGLE_TXT.txt$' # ?
            for f in file_list:
                try:
                    file_of_interest2 = re.match(pattern3, f).group(0)
                except AttributeError:
                    continue # I think?

            if not file_of_interest1 or not file_of_interest2:
                continue # skip? since we will not be able to get data
            file_of_interest1 = os.path.join(os.getcwd(), local_temp_dir, file_of_interest1)
            file_of_interest2 = os.path.join(os.getcwd(), local_temp_dir, file_of_interest2)
            merchant_file_pairs.append((merchant_name, file_of_interest1, file_of_interest2))

        # this way we will run ir once for each found pair (altho currently only 1)
        for file_pair in merchant_file_pairs:
            print file_pair
            merchant_name = file_pair[0].decode('UTF-8')
            merchant_id = product_feed_helpers.generate_merchant_id(merchant_name)
            product_catalog_IR = file_pair[1]
            product_catalog_GOOGLE = file_pair[2]

            # rewrite the process to use both files
            with open(product_catalog_IR, "r") as file1, open(product_catalog_GOOGLE, "r") as file2:
                lines1 = file1.readlines()
                lines2 = file2.readlines()

                # need some way to identify the merchants??
                merchant_is_active = mappings.is_merchant_active(merchant_id, merchant_name, network, merchant_mapping)
                # merchant_is_active = 1
                if merchant_is_active:
                    # config file
                    config_path = BASE_DIR + '/tasks/product_feed_py/merchants_config/impact_radius/'
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

                    # omit fieldnames to use header lines
                    reader1 = csv.DictReader(lines1, restval = '', dialect = 'reading')
                    reader2 = csv.DictReader(lines2, restval = '', dialect = 'reading')

                    for datum1, datum2 in izip(reader1, reader2): # handle when/if the files are of two different lengths
                        totalCount += 1

                        # unicode sandwich stuff
                        for key, value in datum1.iteritems():
                            datum1[key] = value.decode('UTF-8')
                        for key, value in datum2.iteritems():
                            datum2[key] = value.decode('UTF-8')

                        # gender pigeonholing
                        gender = datum1['Gender']
                        gender = gender.upper()
                        gender = gender.replace('FEMALE', 'WOMEN')
                        gender = gender.replace('MALE', 'MEN')
                        gender = gender.replace('MAN', 'MEN')

                        # gender checking
                        skippedGenders = ['MEN', 'CHILD', 'KIDS', 'BOYS', 'GIRLS', 'BABY']
                        if gender in skippedGenders:
                            genderSkipped += 1
                            continue

                        primary_category = datum1['Category']
                        secondary_category = product_feed_helpers.product_field_tiered_assignment(tiered_assignments, 'secondary_category', datum1, u'', synonym_category_mapping = synonym_category_mapping, synonym_other_category_mapping = synonym_other_category_mapping, exclusion_terms = exclusion_terms)

                        allume_category = mappings.are_categories_active(primary_category, secondary_category, category_mapping, allume_category_mapping, merchant_name, exclusion_terms, synonym_other_terms, synonym_terms)
                        # allume_category = 'allume_category'
                        if allume_category:
                            record = {}

                            record['merchant_color'] = datum1['Color']
                            merchant_color = datum1['Color'].lower()
                            try:
                                allume_color = color_mapping[merchant_color]
                            except:
                                allume_color = u'other'
                            record['color'] = allume_color

                            #datum1
                            record['age'] = datum1['Age Range']
                            record['manufacturer_name'] = datum1['Manufacturer']
                            record['long_product_description'] = datum1['Product Description']
                            record['short_product_description'] = datum1['Product Description']
                            record['product_name'] = datum1['Product Name']

                            size = datum1['Size'].upper()
                            size = size.replace('~', ',')
                            record['size'] = size
                            record['allume_size'] = product_feed_helpers.determine_allume_size(allume_category, size, size_mapping, shoe_size_mapping, size_term_mapping)

                            record['manufacturer_part_number'] = datum1['MPN']
                            record['product_type'] = datum1['Product Type']
                            record['gender'] = gender
                            record['product_url'] = datum1['Product URL']
                            record['product_image_url'] = datum1['Image URL']
                            record['primary_category'] = primary_category
                            record['SKU'] = datum1['Unique Merchant SKU']

                            current_price = datum1['Current Price']
                            record['current_price'] = current_price
                            record['sale_price'] = current_price
                            record['retail_price'] = current_price

                            record['shipping_price'] = datum1['Shipping Rate']
                            record['material'] = datum1['Material']

                            #datum2
                            record['product_id'] = datum2['custom_label_4'] # there is an instance of custom_label_3 having the product_id
                            # handling product_id in one of the custom labels
                            for i in range(0, 5):
                                key = 'custom_label_' + str(i)
                                if datum2[key].isdigit(): # product_id can seemingly occur at place 3 or 4
                                    record['product_id'] = datum2[key]
                                    break
                            if not record['product_id']: # it did not get set in above
                                record['product_id'] = product_feed_helpers.generate_product_id(record['product_name'], size, merchant_color, record['SKU'])

                            availability = datum2['availability']
                            availability = availability.replace(' ', '-')

                            if availability == '' or availability == 'no':
                                availability = u'out-of-stock'
                            elif availability == 'yes':
                                availability = u'in-stock'
                            record['availability'] = availability

                            record['brand'] = datum2['brand']

                            # derived
                            try:
                                record['raw_product_url'] = product_feed_helpers.parse_raw_product_url(record['product_url'], 'u')
                            except KeyError as e:
                                print e
                                record['raw_product_url'] = u''
                            record['allume_category'] = allume_category

                            # not from data
                            record['merchant_name'] = merchant_name
                            record['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S').decode('UTF-8')
                            # defaults?
                            record['is_best_seller'] = u'0'
                            record['is_trending'] = u'0'
                            record['allume_score'] = unicode(merchant_search_rank_mapping[long(merchant_id)])
                            # need to infer deleted?
                            record['is_deleted'] = u'0'

                            # not sure how this will go
                            record['merchant_id'] = merchant_id

                            # fields not available from data?
                            record['buy_url'] = u''
                            record['discount'] = u''
                            record['discount_type'] = u''
                            record['style'] = u''
                            record['currency'] = u''
                            record['keywords'] = u''
                            record['secondary_category'] = secondary_category




                            # size splitting stuff
                            parent_attributes = copy(record)
                            sizes = product_feed_helpers.seperate_sizes(parent_attributes['size'])
                            product_id = parent_attributes['product_id']
                            if len(sizes) > 1: # the size attribute of the record was a comma seperated list
                                for size in sizes:
                                    child_record = copy(parent_attributes)
                                    child_record['allume_size'] = product_feed_helpers.determine_allume_size(allume_category, size, size_mapping, shoe_size_mapping, size_term_mapping)
                                    # use the size mapping here also

                                    child_record['size'] = size
                                    child_record['product_id'] = product_feed_helpers.assign_product_id_size(product_id, size)
                                    for key, value in child_record.iteritems():
                                        child_record[key] = value.encode('UTF-8')

                                    writer.writerow(child_record)
                                    writtenCount += 1
                                # set the parent record to is_deleted
                                record['is_deleted'] = u'1'

                            # finish unicode sandwich
                            for key, value in record.iteritems():
                                record[key] = value.encode('UTF-8')

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

    # infer deleted products
    # print('Updating non-upserted Impact Radius products')
    # product_feed_helpers.set_deleted_network_products('Impact Radius')


