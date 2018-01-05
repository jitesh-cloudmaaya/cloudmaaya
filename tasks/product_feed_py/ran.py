import os
import datetime
from django.db import connection
from . import mappings

### attempt at writing record with logic
def clean_ran(local_temp_dir):
    # instantiate relevant mappings
    merchant_mapping = mappings.create_merchant_mapping()
    color_mapping = mappings.create_color_mapping()
    category_mapping = mappings.create_category_mapping()
    allume_category_mapping = mappings.create_allume_category_mapping()

    destination = local_temp_dir + '/cleaned/flat_file.txt'
    with open(destination, "w") as cleaned:
        file_list = []
        file_directory = os.listdir(local_temp_dir)

        # could this be moved to configuration file

        # EXTENSIONS = ('.txt') # in the future?

        # EXTENSIONS = ('mp_delta.txt') # eventually change this to .txt only?

        EXTENSIONS = ('mp.txt') # for full files


        for f in file_directory:
            if f.endswith(EXTENSIONS):
                file_list.append(os.path.join(os.getcwd(), local_temp_dir, f))

        totalCount = 0
        writtenCount = 0

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
                    for line in lines:
                        totalCount += 1

                        # unicode sandwich
                        line = line.decode('utf-8')
                        line = line.split('|')

                        # breaking down the data from the merchant files
                        product_id = line[0]
                        product_name = line[1]
                        SKU = line[2]
                        primary_category = line[3]
                        secondary_category = line[4]
                        product_url = line[5]
                        product_image_url = line[6]
                        buy_url = line[7]
                        short_product_description = line[8]
                        long_product_description = line[9]
                        discount = line[10]
                        discount_type = line[11]
                        sale_price = line[12]
                        retail_price = line[13]
                        begin_date = line[14]
                        end_date = line[15]
                        brand = line[16]
                        shipping = line[17]
                        keywords = line[18]
                        manufacturer_part_number = line[19]
                        manufacturer_name = line[20]
                        shipping_information = line[21]
                        availability = line[22]
                        universal_product_code = line[23]
                        class_ID = line[24]
                        currency = line[25]
                        M1 = line[26]
                        pixel = line[27]
                        attribute_1_misc = line[28]
                        attribute_2_product_type = line[29]
                        attribute_3_size = line[30]
                        attribute_4_material = line[31]
                        attribute_5_color = line[32]
                        attribute_6_gender = line[33]
                        attribute_7_style = line[34]
                        attribute_8_age = line[35]
                        attribute_9 = line[36]

                        # in a delta file, there is 1 additional field for modification
                        attribute_10 = line[37].rstrip('\n') # account for other line endings?
                        try:
                            modification = line[38].rstrip('\n') # account for other line endings?
                        except:
                            modification = ''

                        # moving gender check above categories check
                        # as all men categories have no entries in category tables
                        gender = attribute_6_gender.upper()
                        gender = gender.replace('FEMALE', 'WOMEN')
                        gender = gender.replace('MALE', 'MEN')
                        gender = gender.replace('MAN', 'MEN')
                        # check if gender makes record 'inactive'
                        if gender == 'MEN' or gender == 'CHILD' or gender == 'KIDS': # girls and boys?
                            continue


                        try:
                            identifier = (primary_category, secondary_category)
                            allume_category_id, active = category_mapping[identifier]
                            # activity check on the primary, secondary category pair
                            if not active:
                                continue
                            # print(active)
                            allume_category, active = allume_category_mapping[allume_category_id]
                            # activity check on the allume_category
                            if not active:
                                continue
                        except:
                            # there is no entry in the category tables for the provided categories
                            # assume inactive?
                            continue


                        # logic for constructing record for product_api_product
                        record = ''
                        record += product_id + u'|'
                        record += merchant_id + u'|'
                        record += product_name + u'|'
                        record += long_product_description + u'|'
                        record += short_product_description + u'|'
                        record += product_url + u'|'
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
                            record += "Other|"
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
                else:
                    # print("is not active")
                    pass

    print('Processed %s records' % totalCount)
    print('Wrote %s records' % writtenCount)



