import os
import datetime
import yaml
import urlparse
from django.db import connection
from . import mappings
from catalogue_service.settings import BASE_DIR



# discover unmapped categories and merchants as a method
# there is a network model in product_api, in pepperjam this is used to add merchants with a network id of pepperjam
# for ran, something similar should occur where discovered merchants that are added have a network id correspodning to RAN
# pepperjam gets the merchants using the api url
# a varible to count process metrics
# then for each merchant in the data, he checks if it is in the mapping table,
# if it is not, he adds a corresponding merchant object
# and then recreates the merchant_mapping
# suggestion is to have a global mappings table that is generated once and added to and reference throughout life of program
# something similar for category map?

### attempt at writing record with logic
def clean_ran(local_temp_dir, file_ending):
    # instantiate relevant mappings
    merchant_mapping = mappings.create_merchant_mapping()
    color_mapping = mappings.create_color_mapping()
    category_mapping = mappings.create_category_mapping()
    allume_category_mapping = mappings.create_allume_category_mapping()


    # check the lengths of the category mapping after two passes on the same data
    print '##################  LENGTH #############################'
    print len(category_mapping)
    print '##################  EnD #############################'

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

        pendingReviewSkipped = 0
        categoriesDiscovered = 0

        # iterate only over the .txt files
        for f in file_list:

            with open(f, "r") as f: #, open('temp.txt', 'r') as test:
                header = f.readline()
                header = header.decode('utf-8')
                header = header.split('|')
                merchant_id = header[1]
                merchant_name = header[2]

                lines = f.readlines()
                lines = lines[:-1]

                # handle if merchant_id not in merchant_table?
                try:
                    merchant_is_active = merchant_mapping[int(merchant_id)]
                except:
                    merchant_is_active = 0
                # check that the merchant_id is active in the merchant mapping
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
                        config_dict = config_dict['fields'][0]

                    for line in lines:
                        totalCount += 1

                        # unicode sandwich
                        line = line.decode('utf-8')
                        line = line.split('|')

                        # breaking down the data from the merchant files
                        product_id = line[config_dict['product_id']]
                        product_name = line[config_dict['product_name']]
                        SKU = line[config_dict['SKU']]
                        primary_category = line[config_dict['primary_category']]
                        secondary_category = line[config_dict['secondary_category']]
                        product_url = line[config_dict['product_url']]


                        # implement cheap fix for now, change when migrating to python's csv library
                        try:
                            raw_product_url = urlparse.parse_qs(urlparse.urlsplit(product_url).query)['murl'][0]
                            raw_product_url = raw_product_url.replace('|', '%7C') # look this over again when csv lib
                        except:
                            raw_product_url = '' # there was an error of some kind

                        product_image_url = line[config_dict['product_image_url']]
                        buy_url = line[config_dict['buy_url']]
                        short_product_description = line[config_dict['short_product_description']]
                        long_product_description = line[config_dict['long_product_description']]
                        discount = line[config_dict['discount']]
                        if not discount:
                            discount = '0.00'
                        discount_type = line[config_dict['discount_type']]
                        sale_price = line[config_dict['sale_price']]
                        if not sale_price:
                            sale_price = '0.00'
                        retail_price = line[config_dict['retail_price']]
                        begin_date = line[config_dict['begin_date']]
                        end_date = line[config_dict['end_date']]
                        brand = line[config_dict['brand']]
                        shipping = line[config_dict['shipping']]
                        if not shipping:
                            shipping = '0.00'
                        keywords = line[config_dict['keywords']]
                        manufacturer_part_number = line[config_dict['manufacturer_part_number']]
                        manufacturer_name = line[config_dict['manufacturer_name']]
                        shipping_information = line[config_dict['shipping_information']]
                        availability = line[config_dict['availability']]
                        universal_product_code = line[config_dict['universal_product_code']]
                        class_ID = line[config_dict['class_ID']]
                        currency = line[config_dict['currency']]
                        M1 = line[config_dict['M1']]
                        pixel = line[config_dict['pixel']]

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

                        # category map discovery stuff
                        # rather than recreating the mapping for every record with a new mapping
                        # let's change it to a method that checks for its existance,
                        # adding it to a global mapping variable that is generated once if otherwise


                        def checkCategoryMap(primary_category, secondary_category):
                            """
                            Takes in both a primary_category and secondary_category and checks for its
                            existance in CategoryMap, discovering it otherwise.
                            """
                            # isn't it essentially
                            # (primary_category, secondary_category) in category_mapping?
                            pass

                        # new process
                        # call a function that checks for the (primary_category, secondary_category)
                        # try:
                        # identifier in the current_category_mappings
                        identifier = (primary_category, secondary_category)
                        # checkCategoryMap(primary_category, secondary_category)
                        if identifier not in category_mapping.keys():
                            # if it does not exist, add it both django/db
                            mappings.add_category_map(primary_category, secondary_category, None, False, True)
                            # and mapping instance
                            category_mapping[identifier] = (None, 0)
                            # print the category pair we 'discovered'
                            print identifier
                            # increment a discovered variable metric
                            categoriesDiscovered += 1

                            # even if we skip the newly added category here, other occurences will still cause a None error

                        allume_category_id, active = category_mapping[identifier]
                        if not allume_category_id:
                            # it is None because it is a newly discovered category
                            # or a category that is still pending review
                            pendingReviewSkipped += 1
                            continue
                        # activity check on primary, secondary category pair
                        if not active:
                            inactiveSkipped += 1
                            continue
                        allume_category, active = allume_category_mapping[allume_category_id]
                        # activity check on the allume_category
                        if not active:
                            inactiveSkipped += 1
                            continue
                        # except Exception as e:
                            # raise e

                            # key error in either category_mapping or allume_category_mapping
                            # print 'somehow an identifier without an entry was accessed'
                            # print e
                            # continue



#                         try:
#                             identifier = (primary_category, secondary_category)
#                             allume_category_id, active = category_mapping[identifier]
#                             # activity check on the primary, secondary category pair
#                             if not active:
#                                 inactiveSkipped += 1
#                                 continue
#                             # print(active)
#                             allume_category, active = allume_category_mapping[allume_category_id]
#                             # activity check on the allume_category
#                             if not active:
#                                 inactiveSkipped += 1
#                                 continue
#                         except:
#                             # there is no entry in the category tables for the provided categories
#                             # assume inactive?


# # +----+-----------------------+-------------------------+--------+------------+------------+--------------------+----------------+
# # | id | external_cat1         | external_cat2           | active | created_at | updated_at | allume_category_id | pending_review |
# # +----+-----------------------+-------------------------+--------+------------+------------+--------------------+----------------+
# # |  1 | Apparel & Accessories | Clothing~~Shirts & Tops |      1 | NULL       | NULL       |                  1 |              0 |
# # |  2 | Apparel & Accessories |                         |      1 | NULL       | NULL       |                  2 |              0 |
# # |  3 | Apparel & Accessories | Clothing~~Pants         |      1 | NULL       | NULL       |                  3 |              0 |
# # |  4 | Apparel & Accessories | Shoes                   |      1 | NULL       | NULL       |                  4 |              0 |
# # |  5 | Apparel & Accessories | Clothing~~Dresses       |      1 | NULL       | NULL       |                  5 |              0 |
# # +----+-----------------------+-------------------------+--------+------------+------------+--------------------+----------------+

#                             #################### MY ATTEMPT #################################

#                             # call as a function?
#                             # e.g. # checkCategory(primary_category, secondary_category)

#                             # update the categorymap instance to include this category
#                             category_mapping[(primary_category, secondary_category)] = None # intialize with allume_cat_id of None

#                             # create the category map in django/db
#                             CategoryMap.objects.create(primary_category, secondary_category, None, False, True)

#                             # instead of allumecategorySkipped
#                             # categoriesDiscovered += 1

#                             #################### END MY ATTEMPT #############################

#                             # add the unmappped category to the mappings table
#                             ##################### FROM PEPPERJAM ############################

#                             mappings.add_category_map(primary_category, secondary_category, None, False, True)
#                             allume_category_mapping = mappings.create_allume_category_mapping()
#                             category_mapping = mappings.create_category_mapping()

#                             ##################### END FROM PEPPERJAM ########################
# # def add_category_map(external_cat1, external_cat2, allume_category, active = False, pending_review=True):
# #     CategoryMap.objects.create(external_cat1 = external_cat1, external_cat2 = external_cat2, 
# #                                allume_category = None, active = active, pending_review=pending_review)


#                             allumecategorySkipped += 1
#                             continue


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
    print('Discovered %s unmapped primary and secondary category pairs' % categoriesDiscovered)
    print('Dropped %s records due to pending discovered categories' % pendingReviewSkipped) 
    print('Dropped %s records due to gender' % genderSkipped)
    # print('Dropped %s records due to no allume_category_id mapping' % allumecategorySkipped)
    print('Dropped %s records due to inactive categories' % inactiveSkipped)



