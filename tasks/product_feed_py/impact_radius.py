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

        csv.register_dialect('reading', delimiter='|', quoting=csv.QUOTE_NONE, quotechar='')
        csv.register_dialect('writing', delimiter=',', quoting=csv.QUOTE_ALL, quotechar='"', doublequote=False, escapechar='\\', lineterminator='\n')

        cleaned_fieldnames = cleaned_fields.split(',')
        writer = csv.DictWriter(cleaned, cleaned_fieldnames, dialect = 'writing')








# need to add helper to infer deleted status
def set_deleted_impact_radius_products(threshold = 12):
    pass