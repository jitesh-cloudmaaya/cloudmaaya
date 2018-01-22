import os
import ftplib
import re
import zipfile
import subprocess
from django.db import connection, transaction
import yaml
import datetime
from product_feed_py import *

from catalogue_service.settings import BASE_DIR

class ProductFeed(object):


    def __init__(self, config_file):
        
        config_file = open(config_file, "r")
        config_dict = yaml.load(config_file)
        self._table = config_dict['table']
        self._fields = ",".join(config_dict['fields'])
        self._fields = " (%s) " % (self._fields)
        self._file_pattern = config_dict['file_pattern']
        self._ftp_host = config_dict['ftp_config']['host']
        self._ftp_user = config_dict['ftp_config']['user']
        self._ftp_password = config_dict['ftp_config']['password'] 
        self._local_temp_dir = config_dict['local_temp_dir'] if config_dict['local_temp_dir'] else settings_local.PRODUCT_FEED_TEMP
        self._remote_dir = config_dict['remote_dir']
        self._remote_files = []
        self._leave_temp_files = config_dict['leave_temp_files']
        self.etl_file_name = config_dict['etl_file_name']
        self._local_temp_dir_cleaned = self._local_temp_dir + '/cleaned'
        self._clean_data_method = config_dict['clean_data_method']
        self._file_ending = config_dict['file_ending']


    ### space for my additions

    def clean_data(self):
        exec self._clean_data_method


    # cursor = connection.cursor()
    # etl_file = open(os.path.join(BASE_DIR, 'tasks/client_360_sql/client_360.sql'))
    # statement = etl_file.read()
    # cursor.execute(statement)


    # how to get filename of flat_file.csv
    def load_cleaned_data(self): # eventually rename
        cursor = connection.cursor()

        # filepath to pd_temp/ran/cleaned/flat_file.csv ?
        file_list = os.listdir(self._local_temp_dir_cleaned)
        f = file_list[0] # corresponds to flat_file.csv
        f = os.path.join(os.getcwd(), self._local_temp_dir_cleaned, f)
        table = self._table
        fields = self._fields

        # table = temporary/intermediate table
        # statement = "DELETE FROM product_api_product WHERE temp_table.product_id = product_api.product_id"
        # statement = "INSERT INTO"

        # separate current temp sql thingy into two files
        sql_script = open(os.path.join(BASE_DIR, 'tasks/mv-script-somewhere.sql'))
        statement = sql_script.read()
        print 'creating temp table'
        cursor.execute(statement)
        cursor.close()

        cursor = connection.cursor()

        print 'loading cleaned data to temp table'
        table = 'product_api_product_temp'
        statement = "LOAD DATA LOCAL INFILE '%s' INTO TABLE %s FIELDS TERMINATED BY '|' %s;" % (f, table, fields)
        cursor.execute(statement)

        cursor.close()

        cursor = connection.cursor()

        # hopefully two parts works with .execute for now
        sql_script = open(os.path.join(BASE_DIR, 'tasks/mv-script-somewhere-2.sql'))
        statement = sql_script.read()
        print 'delete and insert for update'
        cursor.execute(statement)

        cursor.close()

        print 'finished'

    def decompress_data(self):
        file_list = os.listdir(self._local_temp_dir)

        for remote_file in file_list:

            local_file = os.path.join(os.getcwd(), self._local_temp_dir, remote_file)

            if "zip" in local_file:
                local_file = self.unzip(local_file)

            if "gz" in local_file:
                local_file = self.ungzip(local_file)


    ### end space for additions

    def make_temp_dir(self):
        if not os.path.exists(self._local_temp_dir):
            os.makedirs(self._local_temp_dir)
        if not os.path.exists(self._local_temp_dir_cleaned):
            os.makedirs(self._local_temp_dir_cleaned)


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



