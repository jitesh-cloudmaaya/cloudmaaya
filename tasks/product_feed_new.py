import os
import ftplib
import re
import zipfile
import subprocess
from django.db import connection, transaction
import yaml
import datetime

class ProductFeed(object):


    def __init__(self, config_file):
        
        config_file = open(config_file, "r")
        config_dict = yaml.load(config_file)
        self._table = config_dict['table']
        self._fields = ",".join(config_dict['fields'])
        self._file_pattern = config_dict['file_pattern']
        self._ftp_host = config_dict['ftp_config']['host']
        self._ftp_user = config_dict['ftp_config']['user']
        self._ftp_password = config_dict['ftp_config']['password'] 
        self._local_temp_dir = config_dict['local_temp_dir'] if config_dict['local_temp_dir'] else settings_local.PRODUCT_FEED_TEMP
        self._local_temp_dir_cleaned = self._local_temp_dir + '/cleaned'
        self._remote_dir = config_dict['remote_dir']
        self._remote_files = []
        self._leave_temp_files = config_dict['leave_temp_files']
        self.etl_file_name = config_dict['etl_file_name']


    ### space for my additions
    def make_cleaned_dir(self):
        if not os.path.exists(self._local_temp_dir_cleaned):
            os.makedirs(self._local_temp_dir_cleaned)

    def create_merchant_mapping(self):
        cursor = connection.cursor()
        cursor.execute("SELECT external_merchant_id, active FROM product_api_merchant")

        merchant_mapping = {}
        for tup in cursor.fetchall():
            merchant_mapping[tup[0]] = tup[1]

        return merchant_mapping


    def create_color_mapping(self):
        cursor = connection.cursor()
        cursor.execute("SELECT external_color, allume_color FROM product_api_colormap")

        color_mapping = {}
        for tup in cursor.fetchall():
            color_mapping[tup[0]] = tup[1]

        return color_mapping

    # def read_merchant_file(self, remote_file):
    # def process_merchant_file(self):
    #     file_list = os.listdir(self._local_temp_dir) # will grap .txt, /cleaned, and 2 .gz files
        

    #     relevant_file = file_list[1] # currently gets 13816_3389478_mp_delta.txt
    #     relevant_file = os.path.join(os.getcwd(), self._local_temp_dir, relevant_file)
    #     print(relevant_file)
    #     # need to get the merchant_id and add to every line in the file

    #     # in theory we would do this in a for loop for every file
    #     # also need to check the merchant name against whether or not they are 'active'
    #     download_dir = self._local_temp_dir + '/cleaned/flat_file.txt'
    #     with open(relevant_file, "r") as f:
    #         with open(download_dir, "w") as csv:
    #             csv.write('product_id|product_name|SKU|primary_category|secondary_category|produdct_url|product_image_url|buy_url|short_product_description|long_product_description|discount|discount_type|sale_price|retail_price|begin_date|end_date|brand|shippping|keywords|manufacturer_part_number|manufacturer_name|shipping_information|availablity|universal_product_code|class_id|currency|M1|pixel|attribute_1_misc|attribute_2_product_type|attribute_3_size|attribute_4_material|attribute_5_color|attribute_6_gender|attribute_7_style|attribute_8_age|attribute_9|attribute_10|attribute_11|merchant_id\n')
    #             header = f.readline()
    #             merchant_id = header.split('|')[1]
    #             for line in f:
    #                 line = line.strip('\n') 
    #                 line += "|" + merchant_id
    #                 # line = line.replace('|', ',') # data has commas?
    #                 line += '\n'
    #                 csv.write(line)
    #     print('FINISHED')



    # WRITE HELPER FOR processing individual merchant file?

    ### attempt at writing record with logic
    def clean_data(self):
        # self.make_cleaned_dir()

        # instantiate color mapping and merchant mappings
        merchant_mapping = self.create_merchant_mapping()
        color_mapping = self.create_color_mapping()

        destination = self._local_temp_dir + '/cleaned/flat_file.csv'
        with open(destination, "w") as cleaned:
            fields = 'product_id,merchant_id,product_name,long_product_description,short_product_description,product_url,product_image_url,buy_url,manufacturer_name,manufacturer_part_number,SKU,product_type,discount,discount_type,sale_price,retail_price,shipping_price,color,gender,style,size,material,age,currency,availability,keywords,primary_category,secondary_category,brand,updated_at,merchant_name,is_best_seller,is_trending,allume_score,current_price,is_deleted\n'
            cleaned.write(fields)
            print(len(self._fields.split(',')))
            print(self._fields.split(','))
            print(len(fields.split(',')))
            print(fields.split(','))

            file_list = os.listdir(self._local_temp_dir)
            # for file in file_list
            f = file_list[1]
            f = os.path.join(os.getcwd(), self._local_temp_dir, f)
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
                    attribute_11 = line[38]

                    # potentially add enclosed by
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
                    record += '|'
                    record += '|'
                    record += '|'

                    # need to comp as floats
                    # wrap in try?
                    try:
                        if float(sale_price) > 0: # OR NOT NULL ??
                            record += sale_price + '|'
                        else:
                            record += retail_price + '|'
                    except:
                        record += '|' # ?

                    record += '\n' # final column doesn't need a comma?


                    # write the reconstructed line to the cleaned file
                    cleaned.write(record)
                    print(len(record.split('|')))
                    print(record.split('|'))
                    break # remove when ready to test on larger dataset


# how to get filename of flat_file.csv
def test_load_cleaned_data(self, file_name):
    print('running')
    cursor = connection.cursor()
    fields = self._fields
    fields = " (%s) " % (fields)

    # filepath to pd_temp/ran/cleaned/flat_file.csv ?
    file_list = os.listdir(self._local_temp_dir + '/cleaned')
    f = file_list[0]
    f = os.path.join(os.getcwd(), self._local_temp_dir + '/cleaned', f)

    # LINES TERMINATED BY '\n'
    statement = "LOAD DATA LOCAL INFILE '%s' INTO TABLE %s FIELDS TERMINATED BY ',' IGNORE 1 LINES %s;" % (f, self._table, fields)
    cursor.execute(statement)
    print('success')

# def load_data_statement(self, file_name, table, fields):
#     if fields:
#         fields = " (%s) " % (fields)
#     statement = "LOAD DATA LOCAL INFILE '%s' INTO TABLE %s FIELDS TERMINATED BY '|' IGNORE 1 LINES %s;" % (file_name, table, fields)
#     return statement

    # def write_to_csv(self, local_file)
    # def write_to_csv(self):
    #     download_dir = self._local_temp_dir + 'flat_file.csv'
    #     # self._fields is a string of fields, separated by commas
    #     with open(download_dir, "w") as csv:
    #         csv.write(self._fields + "\n") # writes the headers

    #     print('occurs')





    ### end space for additions

    def make_temp_dir(self):
        if not os.path.exists(self._local_temp_dir):
            os.makedirs(self._local_temp_dir)

    def get_files_ftp(self):

        self.make_temp_dir()
        ftp = ftplib.FTP(self._ftp_host)
        ftp.login(self._ftp_user, self._ftp_password)
        ftp.cwd(self._remote_dir) 

        regex=re.compile(self._file_pattern)
        self._remote_files = [m.group(0) for file in ftp.nlst() for m in [regex.search(file)] if m]
        for remote_file in self._remote_files:
            local_file = os.path.join(self._local_temp_dir, remote_file)
            ftp.retrbinary("RETR " + remote_file ,open(local_file, 'wb').write)
 
        ftp.quit()

    def process_data(self):

        #Truncate the Target Table
        self.truncate_db_table()

        file_list = os.listdir(self._local_temp_dir)

        for remote_file in file_list:

            local_file = os.path.join(os.getcwd(), self._local_temp_dir, remote_file)

            if "zip" in local_file:
                local_file = self.unzip(local_file)

            if "gz" in local_file:
                local_file = self.ungzip(local_file)



            # my logic inserted here, process each text file?



            # Load the Data into MySQL with Load Data Infile
            self.load_data(local_file)

            #Update Data Once in the DB Table, for RAN update the merchant_id column
            self.load_data_post_process(remote_file)

            if not self._leave_temp_files:
                self.remove_temp_file(local_file)

    def update_products_api(self):
        cursor = connection.cursor()
        etl_file = open(self.etl_file_name)
        statement = etl_file.read()
        cursor.execute(statement)

    def truncate_db_table(self):
        cursor = connection.cursor()
        statement = "TRUNCATE TABLE %s" % (self._table)
        cursor.execute(statement)

    def load_data(self, local_file):
        cursor = connection.cursor()
        statement = self.load_data_statement(local_file, self._table, self._fields)
        print statement
        cursor.execute(statement)

    def load_data_post_process(self, remote_file):

        merchant_id = remote_file.split("_")[0]
        print "%s - %s" % (remote_file, merchant_id)

        cursor = connection.cursor()
        statement = "UPDATE %s SET merchant_id = %s WHERE merchant_id IS NULL;" % (self._table, merchant_id)
        cursor.execute(statement)       

    def remove_temp_file(self, filename):
        try:
            os.remove(filename)
        except OSError:
            pass

    def load_data_statement(self, file_name, table, fields):
        if fields:
            fields = " (%s) " % (fields)
        statement = "LOAD DATA LOCAL INFILE '%s' INTO TABLE %s FIELDS TERMINATED BY '|' IGNORE 1 LINES %s;" % (file_name, table, fields)
        return statement

    def unzip(self, gz_file):
        zipfile.ZipFile(gz_file).extractall()
        return file.replace(".zip", "")

    def ungzip(self, gz_file):
        print gz_file
        os.system("gunzip -f %s" % (gz_file))
        self.remove_temp_file(gz_file)
        return gz_file.replace(".gz", "")

"""

from tasks.product_feed import ProductFeed
table_fields = 'product_id, product_name, SKU, primary_category, secondary_category, product_url, product_image_url, buy_url, short_product_description, long_product_description, discount, discount_type, sale_price, retail_price, begin_date, end_date, brand, shippping, keywords, manufacturer_part_number, manufacturer_name, shipping_information, availablity, universal_product_code, class_id, currency, M1, pixel, attribute_1_misc, attribute_2_product_type, attribute_3_size, attribute_4_material, attribute_5_color, attribute_6_gender, attribute_7_style, attribute_8_age, attribute_9, attribute_10, attribute_11, attribute_12, attribute_13, attribute_14, attribute_15 ,attribute_16 ,attribute_17 ,attribute_18 ,attribute_19 ,attribute_20 ,attribute_21 ,attribute_22 ,modification ,merchant_id'
pf = ProductFeed('tasks_ranproducts', table_fields, {'host': 'aftp.linksynergy.com', 'user': 'allumestye', 'password': 'yT%6-Pl@h'}, 'pd_temp/ran', '/', False, ".*_mp_delta\.txt\.gz")
pf.get_files_ftp()
pf.process_data()

"""



