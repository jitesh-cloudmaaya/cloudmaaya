import os
import datetime
import yaml
import urlparse
import csv
from . import mappings, product_feed_helpers
from catalogue_service.settings import BASE_DIR
from product_api.models import Merchant, CategoryMap

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
        with open(product_catalog_IR, "r") as csvfile:
            # header = csvfile.readline()
            # header = header.decode('UTF-8')
            # header = header.split('\t')

            # print header

            lines = csvfile.readlines()
            # lines = lines[-1]

            # need to figure out how or if to use catalog_GOOGLE_TXT.txt?

            # merchant_is_active = mappings.is_merchant_active(merchant_id, merchant_name, network, merchant_mapping)
            merchant_is_active = 1
            if merchant_is_active:
                reader = csv.DictReader(lines, restval = '', dialect = 'reading') # omit fieldnames to use header
                for datum in reader:
                    totalCount += 1

                    for key, value in datum.iteritems():
                        datum[key] = value.decode('UTF-8')

                    for key, value in datum.iteritems():
                        print (key, value)

                    # unpack relevant data and do skipping checks ere


                    # allume_category = mappings.are_categories_active(primary_category, secondary_category, category_mapping, allume_category_mapping, merchant_name)
                    allume_category = 'allume_category'
                    if allume_category:
                        record = {}



                        record['merchant_color'] = datum['Color']
                        merchant_color = datum['Color'].lower()
                        try:
                            allume_color = color_mapping[merchant_color]
                        except:
                            allume_color = u'other'
                        record['color'] = allume_color

                        record['age'] = datum['Age Range']
                        record['manufacturer_name'] = datum['Manufacturer']
                        record['long_product_description'] = datum['Product Description']
                        record['short_product_description'] = datum['Product Description']
                        record['product_name'] = datum['Product Name']
                        record['size'] = datum['Size']

                        print record
                        return




# still need to get these fields
# - product_id
# - merchant_id
# - product_url
# - raw_product_url
# - product_image_url
# - buy_url
# - manufacturer_part_number
# - SKU
# - product_type
# - discount
# - discount_type
# - sale_price
# - retail_price
# - shipping_price
# - gender
# - style
# - material
# - currency
# - availability
# - keywords
# - primary_category
# - secondary_category
# - allume_category
# - brand
# - updated_at
# - merchant_name
# - is_best_seller
# - is_trending
# - allume_score
# - current_price
# - is_deleted

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








