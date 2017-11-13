from django.core.management.base import BaseCommand, CommandError
from catalogue_service.settings_local import DATABASES
from tasks.product_feed import ProductFeed

class Command(BaseCommand):
    help = 'Used to Pull Ran Data Feeds - Incremental Pull'

    def handle(self, *args, **options):
        try:
            table_fields = 'product_id, product_name, SKU, primary_category, secondary_category, product_url, product_image_url, \
                            buy_url, short_product_description, long_product_description, discount, discount_type, sale_price, \
                            retail_price, begin_date, end_date, brand, shippping, keywords, manufacturer_part_number, manufacturer_name, \
                            shipping_information, availablity, universal_product_code, class_id, currency, M1, pixel, attribute_1_misc, \
                            attribute_2_product_type, attribute_3_size, attribute_4_material, attribute_5_color, attribute_6_gender, \
                            attribute_7_style, attribute_8_age, attribute_9, attribute_10, attribute_11, attribute_12, attribute_13, \
                            attribute_14, attribute_15 ,attribute_16 ,attribute_17 ,attribute_18 ,attribute_19 ,attribute_20 ,\
                            attribute_21 ,attribute_22 ,modification ,merchant_id'

            pf = ProductFeed('tasks_ranproducts', table_fields, {'host': 'aftp.linksynergy.com', 'user': 'allumestye', \
                             'password': 'yT%6-Pl@h'}, 'pd_temp/ran', '/', False, ".*_mp_delta\.txt\.gz")

            self.stdout.write(self.style.WARNING("Pulling Files from FTP"))
            pf.get_files_ftp()

            self.stdout.write(self.style.WARNING("Loading Data to DB and Updating Products"))
            pf.process_data()
        except:
            self.stdout.write(self.style.ERROR("Failed"))