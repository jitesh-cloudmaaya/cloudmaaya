import os
import datetime
import yaml
import urlparse
import re
import csv
from . import mappings, product_feed_helpers
from catalogue_service.settings import BASE_DIR
from product_api.models import Merchant, CategoryMap
from itertools import izip

def impact_radius(local_temp_dir, file_ending, cleaned_fields):
    # mappings
    merchant_mapping = mappings.create_merchant_mapping()
    color_mapping = mappings.create_color_mapping()
    category_mapping = mappings.create_category_mapping()
    allume_category_mapping = mappings.create_allume_category_mapping()

    # initialize network instance for adding potential new merchants
    network = mappings.get_network('Impact Radius') # name subject to change?

    destination = local_temp_dir + '/cleaned/ir_flat_file.csv'

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

        csv.register_dialect('reading', delimiter='\t', quoting=csv.QUOTE_NONE, quotechar='')
        csv.register_dialect('writing', delimiter=',', quoting=csv.QUOTE_ALL, quotechar='"', doublequote=False, escapechar='\\', lineterminator='\n')

        cleaned_fieldnames = cleaned_fields.split(',')
        writer = csv.DictWriter(cleaned, cleaned_fieldnames, dialect = 'writing')

        # work with hard coded assumptions for now
        product_catalog_IR = file_list[0] # should be DSW-Product-Catalog_IR.txt
        product_catalog_GOOGLE = file_list[1] # should be DSW-Product-Catalog_GOOGLE_TXT.txt


        # write a regex to get everything before the first hyphen
        # ^(.*?)-
        pattern = re.compile('.*\/(.*?)-')
        result = re.search(pattern, product_catalog_IR) # maybe need to change??
        merchant_name = result.group(1)
        merchant_id = u'432' # hardcoded for now

        # rewrite the process to use both files
        with open(product_catalog_IR, "r") as file1, open(product_catalog_GOOGLE, "r") as file2:
            lines1 = file1.readlines()
            lines2 = file2.readlines()

            # need some way to identify the merchants??
            # merchant_is_active = mappings.is_merchant_active(merchant_id, merchant_name, network, merchant_mapping)
            merchant_is_active = 1
            if merchant_is_active:
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

                    # print statements
                    print '======================= start product %s ===============================' % str(totalCount)
                    print '=================== info from IR ====================='
                    for key, value in datum1.iteritems():
                        print (key, value)
                    print '=================== info from google ================='
                    for key, value in datum2.iteritems():
                        print (key, value)

                    # unpack relevant data and do skipping checks here

                    # allume_category = mappings.are_categories_active(primary_category, secondary_category, category_mapping, allume_category_mapping, merchant_name)
                    allume_category = 'allume_category'
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
                        record['size'] = datum1['Size']
                        record['manufacturer_part_number'] = datum1['MPN']
                        record['product_type'] = datum1['Product Type']
                        record['gender'] = datum1['Gender']
                        record['product_url'] = datum1['Product URL']
                        record['product_image_url'] = datum1['Image URL']
                        record['primary_category'] = datum1['Category']
                        record['SKU'] = datum1['Unique Merchant SKU']
                        record['current_price'] = datum1['Current Price']
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
                            continue # skip this record ???
                            #or generate prod_id somehow
                            # record['product_id'] = generate_product_id(args)
                        record['availability'] = datum2['availability']
                        record['brand'] = datum2['brand']

                        # derived
                        try:
                            record['raw_product_url'] = product_feed_helpers.parse_raw_product_url(record['product_url'], 'u')
                        except Exception as e:
                            print e
                            record['raw_product_url'] = u''
                        record['allume_category'] = allume_category

                        # not from data
                        record['merchant_name'] = merchant_name
                        record['updated_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        # defaults?
                        record['is_best_seller'] = u'0'
                        record['is_trending'] = u'0'
                        record['allume_score'] = u'0'
                        # need to infer deleted?
                        record['is_deleted'] = u'0'


                        # fields not available from data?
                        record['buy_url'] = u''
                        record['discount'] = u''
                        record['discount_type'] = u''
                        record['sale_price'] = u''
                        record['retail_price'] = u''
                        record['style'] = u''
                        record['currency'] = u''
                        record['keywords'] = u''
                        record['secondary_category'] = u''


                        print record



                    print '======================== end product %s ================================' % totalCount
                    if totalCount > 10:
                        return

                        # finish unicode sandwich
                        for key, value in record.iteritems():
                            record[key] = value.encode('UTF-8')

                        # write the record
                        writer.writerow(record)
                        writtenCount += 1
                        return # remove this
                    else:
                        categoriesSkipped += 1

    print('Processed %s records' % totalCount)
    print('Wrote %s records' % writtenCount)
    print('Discovered %s unmapped primary and secondary category pairs' % (CategoryMap.objects.count() - categoryCount))
    print('Discovered %s new merchant(s)' % (Merchant.objects.count() - merchantCount))
    print('Dropped %s records due to gender' % genderSkipped)
    print('Dropped %s records due to inactive categories' % categoriesSkipped)







# need to add helper to infer deleted status
def set_deleted_impact_radius_products(threshold = 12):
    pass








