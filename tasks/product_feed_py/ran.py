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
                    for record in reader:
                        totalCount += 1

                        # do we still need a unicode sandwich?

                        # for key, value in record.iteritems():
                        #     print (key, value)

                        # do unicode sandwich stuff
                        for key, value in record.iteritems():
                            record[key] = value.decode('utf-8')
                        print record
                        return

                        # breaking down the data from the merchant files
                        product_id = record['product_id']
                        product_name = record['product_name']
                        SKU = record['SKU']
                        primary_category = record['primary_category']
                        secondary_category = record['secondary_category']
                        product_url = record['product_url']

                        # implement a cheap fix for now, change when migrating to python's csv library
                        try:
                            raw_product_url = urlparse.parse_qs(urlparse.urlsplit(product_url).query)['murl'][0]
                            raw_product_url = raw_product_url.replace('|', '7%C') # look this over again when csv lib
                        except:
                            raw_product_url = '' # there was an error of some kind

                        product_image_url = record['product_image_url']
                        buy_url = record['buy_url']
                        short_product_description = record['short_product_description']
                        long_product_description = record['long_product_description']
                        discount = record['discount']
                        if not discount:
                            discount = u'0.00' # unicode necessary or not
                        discount_type = record['discount_type']
                        sale_price = record['sale_price']
                        if not sale_price:
                            sale_price = u'0.00' # unicode necessary or not?
                        retail_price = record['retail_price']
                        begin_date = record['begin_date']
                        end_date = record['end_date']
                        brand = record['brand']
                        shipping = record['shipping']
                        if not shipping:
                            shipping = u'0.00' # unicode necessary or not?
                        keywords = record['keywords']
                        manufacturer_part_number = record['manufacturer_part_number']
                        manufacturer_name = record['manufacturer_name']
                        shipping_information = record['shipping_information']
                        availability = record['availability']
                        universal_product_code = record['universal_product_code']
                        class_ID = record['class_ID']
                        currency = record['currency']
                        M1 = record['M1']
                        pixel = record['pixel']

                        # optional attributes begin here
                        # can have different orders
                        # modification must always be at the end (in deltas)
                        attribute_1_misc = record['attribute_1_misc']
                        attribute_2_product_type = record['attribute_2_product_type']
                        attribute_3_size = record['attribute_3_size']
                        attribute_4_material = record['attribute_4_material']
                        attribute_5_color = record['attribute_5_color']
                        attribute_6_gender = record['attribute_6_gender']
                        attribute_7_style = record['attribute_7_style']
                        attribute_8_age = record['attribute_8_age']
                        attribute_9 = record['attribute_9']
                        attribute_10 = record['attribute_10']

                        # in a delta file, there is 1 additional field for modification
                        if record['modification']:
                            modification = record['modification']
                        else: # not a delta file
                            modification = ''

                        # begins attribute manipulation logic
                        print 'kinda sorta successful'



                        break
                  


                        ########## END CSV CONVERSION CODE #######################
                        return
                        ########## BEGIN OLD WAY OF PARSING DATA #################


                        # unicode sandwich
                        line = line.decode('utf-8')
                        line = line.split('|')



                        # optional attributes begin here
                        # can have different orders
                        # modification must always be at the end (in deltas)
                        attribute_1_misc = line[config_dict['attribute_1_misc']]
                        attribute_2_product_type = line[config_dict['attribute_2_product_type']]
                        attribute_3_size = line[config_dict['attribute_3_size']]
                        attribute_4_material = line[config_dict['attribute_4_material']]
                        attribute_5_color = line[config_dict['attribute_5_color']]
                        attribute_6_gender = line[config_dict['attribute_6_gender']]
                        attribute_7_style = line[config_dict['attribute_7_style']]
                        attribute_8_age = line[config_dict['attribute_8_age']]
                        attribute_9 = line[config_dict['attribute_9']]

                        # in a delta file, there is 1 additional field for modification
                        attribute_10 = line[config_dict['attribute_10']].rstrip('\n') # account for other line endings?
                        try:
                            modification = line[config_dict['modification']].rstrip('\n') # account for other line endings?
                        except:
                            modification = ''

                        # moving gender check above categories check
                        # as all men categories have no entries in category tables
                        gender = attribute_6_gender.upper()
                        gender = gender.replace('FEMALE', 'WOMEN')
                        gender = gender.replace('MALE', 'MEN')
                        gender = gender.replace('MAN', 'MEN')

                        # set blanks to proper default?
                        # if not discount:
                        #     discount = '\N'
                        # if not sale_price:
                        #     sale_price = '\N'
                        # if not retail_price:
                        #     retail_price = '\N'
                        # if not shipping:
                        #     shipping = '\N'

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


                        # logic for constructing record for product_api_product
                        record = ''
                        record += product_id + u'|'
                        record += merchant_id + u'|'
                        record += product_name + u'|'
                        record += long_product_description + u'|'
                        record += short_product_description + u'|'
                        record += product_url + u'|'
                        record += raw_product_url + u'|'
                        record += product_image_url + u'|'
                        record += buy_url + u'|'
                        record += manufacturer_name + u'|'
                        record += manufacturer_part_number + u'|'
                        record += SKU + u'|'
                        record += attribute_2_product_type + u'|'
                        if discount_type != "amount" or discount_type != "percentage":
                            record += '0.0|' # how to indicate null or 0 as in sql?
                            record += 'amount|'
                        else:
                            record += discount + u'|'
                            record += discount_type + u'|'
                        record += sale_price + u'|'
                        record += retail_price + u'|'
                        record += shipping + u'|'

                        # current behavior is take the first and find its mapping if possible
                        color = attribute_5_color.split(',')[0].lower()
                        try:
                            record += color_mapping[color] + u'|'
                        except: # where there is no analog
                            record += "other|"
                        record += attribute_5_color + u'|' # merchant color field

                        # gender
                        record += gender + u'|'
                        record += attribute_7_style + u'|'
                        attribute_3_size = attribute_3_size.upper()
                        attribute_3_size = attribute_3_size.replace('~', ',')
                        record += attribute_3_size + u'|'
                        record += attribute_4_material + u'|'
                        attribute_8_age = attribute_8_age.upper()
                        record += attribute_8_age + u'|'
                        record += currency + u'|'
                        if availability == '':
                            availability = 'out-of-stock'
                        record += availability + u'|'
                        record += keywords + u'|'

                        # allume category information
                        record += primary_category + u'|'
                        record += secondary_category + u'|'

                        record += allume_category + u'|'

                        record += brand + u'|'
                        # double check date formatting
                        record += datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + u'|'
                        # record += datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f') + ',') ?
                        # end date
                        record += merchant_name + u'|'
                        # how to indicate null or 0 as in ran.sql
                        record += '0|' # is_best_seller default
                        record += '0|' # is_trending default
                        record += '0|' # allume_score default

                        try:
                            # if there is a sale
                            if float(sale_price) > 0: # OR NOT NULL ??
                                record += sale_price + u'|'
                            else:
                                record += retail_price + u'|'
                        except:
                            record += retail_price + u'|'

                        # is_deleted logic
                        if modification == 'D':
                            record += '1\n' # is this okay given is_deleted is boolean data type
                        else:
                            record += '0\n'
                        # last record needs newline character instead of delimiter

                        # unicode sandwich finish
                        record = record.encode('utf-8')

                        # write the reconstructed line to the cleaned file
                        cleaned.write(record)
                        writtenCount += 1

    print('Processed %s records' % totalCount)
    print('Wrote %s records' % writtenCount)
    print('Dropped %s records due to gender' % genderSkipped)
    print('Dropped %s records due to no allume_category_id mapping' % allumecategorySkipped)
    print('Dropped %s records due to inactive categories' % inactiveSkipped)



