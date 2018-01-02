import os
import datetime
from django.db import connection

def test():
    return

### attempt at writing record with logic
def clean_ran(local_temp_dir):
    # self.make_cleaned_dir()

    # instantiate color mapping and merchant mappings
    merchant_mapping = create_merchant_mapping()
    color_mapping = create_color_mapping()

    destination = local_temp_dir + '/cleaned/flat_file.csv'
    with open(destination, "w") as cleaned:
        fields = 'product_id,merchant_id,product_name,long_product_description,short_product_description,product_url,product_image_url,buy_url,manufacturer_name,manufacturer_part_number,SKU,product_type,discount,discount_type,sale_price,retail_price,shipping_price,color,gender,style,size,material,age,currency,availability,keywords,primary_category,secondary_category,brand,updated_at,merchant_name,is_best_seller,is_trending,allume_score,current_price,is_deleted\n'
        cleaned.write(fields)
        # print(len(self._fields.split(',')))
        # print(self._fields.split(',')) 
        print(len(fields.split(',')))
        print(fields.split(','))

        file_list = os.listdir(local_temp_dir)
        # for file in file_list
        f = file_list[1]
        f = os.path.join(os.getcwd(), local_temp_dir, f)
        print(f)

        with open(f, "r") as f:
            header = f.readline()
            header = header.split('|')
            merchant_id = header[1]
            merchant_name = header[2]
            # check that the merchant_id is active in the merchant mapping
            # if merchant_mapping[merchant_id]: # set the merchant_table active column to 1 for a few companies when testing
            for line in f:
                # need to reconstruct line from merchant file
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
                attribute_10 = line[37]
                modification = line[38].rstrip('\n') # account for other line endings?

                # logic for constructing record for product_api_product
                record = ''
                record += product_id + '|'
                record += merchant_id + '|'
                record += product_name + '|'
                record += long_product_description + '|'
                record += short_product_description + '|'
                record += product_url + '|'
                record += product_image_url + '|'
                record += buy_url + '|'
                record += manufacturer_name + '|'
                record += manufacturer_part_number + '|'
                record += SKU + '|'
                record += attribute_2_product_type + '|'
                if discount_type != "amount" or discount_type != "percentage":
                    record += '|' # how to indicate null or 0 as in sql?
                    record += 'amount|'
                else:
                    record += discount_type + '|'
                    record += discount_type + '|'
                record += sale_price + '|'
                record += retail_price + '|'
                record += shipping + '|'
                try:
                    record += color_mapping[attribute_5_color] + '|'
                except: # where there is no analog
                    record += "Other|"
                # gender replacement
                gender = attribute_6_gender.upper()
                gender = gender.replace('FEMALE', 'WOMEN')
                gender = gender.replace('MALE', 'MEN')
                gender = gender.replace('MAN', 'MEN')
                record += gender + '|'
                # if gender == "FEMALE":
                #     record += "WOMEN,"
                # elif gender == "MALE" or gender == "MAN":
                #     record += "MEN,"
                # else:
                #     record += gender + ','
                record += attribute_7_style + '|'
                attribute_3_size = attribute_3_size.upper()
                attribute_3_size = attribute_3_size.replace('~', ',')
                record += attribute_3_size + '|'
                record += attribute_4_material + '|'
                attribute_8_age = attribute_8_age.upper()
                record += attribute_8_age + '|'
                record += currency + '|'
                if availability == '':
                    availability = 'out-of-stock'
                record += availability + '|'
                record += keywords + '|'
                record += primary_category + '|'
                record += secondary_category + '|'
                record += brand + '|'
                # double check date formatting
                record += datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '|'
                # record += datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f') + ',') ?
                # end date
                record += merchant_name + '|'
                # how to indicate nulll or 0 as in ran.sql
                record += '0|' # is_best_seller default
                record += '0|' # is_trending default
                record += '0|' # allume_score default

                # need to comp as floats
                # wrap in try?
                try:
                    if float(sale_price) > 0: # OR NOT NULL ??
                        record += sale_price + '|'
                    else:
                        record += retail_price + '|'
                except:
                    record += '|' # ?

                # is_deleted logic
                if modification == 'D':
                    record += '1\n' # is this okay given is_deleted is boolean data type
                else:
                    record += '\n'

                # last record needs newline character instead of delimiter

                # write the reconstructed line to the cleaned file
                cleaned.write(record)
                print(len(record.split('|')))
                print(record.split('|'))
                break # remove when ready to test on larger dataset


def create_merchant_mapping():
    cursor = connection.cursor()
    cursor.execute("SELECT external_merchant_id, active FROM product_api_merchant")

    merchant_mapping = {}
    for tup in cursor.fetchall():
        merchant_mapping[tup[0]] = tup[1]

    return merchant_mapping


def create_color_mapping():
    cursor = connection.cursor()
    cursor.execute("SELECT external_color, allume_color FROM product_api_colormap")

    color_mapping = {}
    for tup in cursor.fetchall():
        color_mapping[tup[0]] = tup[1]

    return color_mapping