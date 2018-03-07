import os
import ftplib
import re
import zipfile
import subprocess
from django.db import connection, transaction
import yaml
import datetime
import time
from product_feed_py import *
from catalogue_service.settings import BASE_DIR

class ProductFeed(object):


    def __init__(self, config_file):
        
        config_file = open(config_file, "r")
        config_dict = yaml.load(config_file)
        self._table = config_dict['table']
        self._fields = ",".join(config_dict['fields'])
        # self._fields = " (%s) " % (self._fields)
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


    def clean_data(self):
        start = time.time()
        exec self._clean_data_method
        print "Process takes %s seconds" % (time.time() - start)

    # how to get filename of flat_file.csv
    def load_cleaned_data(self): # eventually rename
        start = time.time()
        cursor = connection.cursor()

        # change the way file list is generated temporarily for pepperjam
        file_list = os.listdir(self._local_temp_dir_cleaned)
        f = file_list[0]
        f = os.path.join(os.getcwd(), self._local_temp_dir_cleaned, f)
        table = self._table
        fields = " (%s) " % (self._fields)

        full_script = []

        sql_script = open(os.path.join(BASE_DIR, 'tasks/product_feed_sql/load-cleaned-data-1.sql'))
        statement = sql_script.read()
        statements = statement.split(';')
        for i in range(0, len(statements)):
            full_script.append(statements[i])

        # need to escape the backslash for python and then also for mySQL
        statement = "LOAD DATA LOCAL INFILE '%s' INTO TABLE %s FIELDS TERMINATED BY ',' ENCLOSED BY '\"' ESCAPED BY '\\\\' LINES TERMINATED BY '\n' %s" % (f, table, fields)
        print statement
        full_script.append(statement)

        sql_script = open(os.path.join(BASE_DIR, 'tasks/product_feed_sql/load-cleaned-data-2.sql'))
        statement = sql_script.read()
        statements = statement.split(';')
        for i in range(0, len(statements)):
            full_script.append(statements[i])

        try:
            with transaction.atomic():
                for i in range(0, len(full_script)):
                    statement = full_script[i]
                    if statement.strip(): # avoid 'query was empty' operational error
                        cursor.execute(statement)
        finally:
            cursor.close()

        print "Process takes %s seconds" % (time.time() - start)

    def decompress_data(self):
        file_list = os.listdir(self._local_temp_dir)

        for remote_file in file_list:

            local_file = os.path.join(os.getcwd(), self._local_temp_dir, remote_file)

            if "zip" in local_file:
                local_file = self.unzip(local_file)

            if "gz" in local_file:
                local_file = self.ungzip(local_file)

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

    def remove_temp_file(self, filename):
        try:
            os.remove(filename)
        except OSError:
            pass

    def unzip(self, gz_file):
        zipfile.ZipFile(gz_file).extractall()
        return file.replace(".zip", "")

    def ungzip(self, gz_file):
        print gz_file
        os.system("gunzip -f %s" % (gz_file))
        self.remove_temp_file(gz_file)
        return gz_file.replace(".gz", "")

