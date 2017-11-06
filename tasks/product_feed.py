import os
import ftplib
import re
from django.db import connection, transaction

class ProductFeed(object):


    def __init__(self, table, fields, ftp_config, local_temp_dir, remote_dir):
        self._table = table
        self._fields = fields
        self._ftp_host = ftp_config['host']
        self._ftp_user = ftp_config['user']
        self._ftp_password = ftp_config['password'] 
        self._local_temp_dir = local_temp_dir
        self._remote_dir = remote_dir
        self._remote_files = []

    def make_temp_dir(self):
        """
        Make Temp Dir for Transferring Files
        """
        if not os.path.exists(self._local_temp_dir):
            os.makedirs(self._local_temp_dir)

    def get_files_ftp(self):

        ftp = ftplib.FTP(self._ftp_host)
        ftp.login(self._ftp_user, self._ftp_password)
        ftp.cwd(self._remote_dir) 

        regex=re.compile(".*_mp\.txt\.gz")
        self._remote_files = [m.group(0) for file in ftp.nlst() for m in [regex.search(file)] if m]
        #print self._remote_files
        for file in self._remote_files:
            print file
            local_file = os.path.join(self._local_temp_dir, file)
            #ftp.retrbinary("RETR " + '41558_3389478_mp.txt.gz' ,open(local_file, 'wb').write)
 
        ftp.quit()

    def load_data(self):
        for file in self._remote_files:
            merchant_id = file.split("_")[0]
            print "%s - %s" % (file, merchant_id)

            #conn = MySQLdb.connect('local_host', 'root', '', 'catalogue_service', local_infile = 1)

            cursor = connection.cursor()

            local_file = os.path.join(os.getcwd(), self._local_temp_dir, file)
            statement = "LOAD DATA LOCAL INFILE '%s' INTO TABLE %s  FIELDS TERMINATED BY '|' IGNORE 1 LINES ;" % (local_file, self._table)
            print statement
            cursor.execute(statement)
            transaction.commit_unless_managed()


"""
for f in *.txt
do
        echo "Loading '"$f"'"
        mid=`echo $f | cut -d'_' -f1`
        mysql --local-infile -u root -e "USE allume_product_feeds; LOAD DATA LOCAL INFILE '"$f"' INTO TABLE ran_product_feed  FIELDS TERMINATED BY '|' IGNORE 1 LINES ;"
        mysql --local-infile -u root -e "USE allume_product_feeds; UPDATE ran_product_feed SET merchant_id = "$mid" WHERE merchant_id IS NULL;"
done


"""

if __name__ == "__main__":
    pf = ProductFeed('tasks_ranproducts', [], {'host': 'aftp.linksynergy.com', 'user': 'allumestye', 'password': 'yT%6-Pl@h'}, 'pd_temp', '/')
    pf.make_temp_dir()
    pf.get_files_ftp()
    pf.load_data()


