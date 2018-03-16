import os
import re
import csv
import yaml
from copy import copy
from . import mappings, product_feed_helpers
from product_api.models import Merchant, CategoryMap

def cj(local_temp_dir, file_ending, cleaned_fields):
    # mappings
    merchant_mapping = mappings.create_merchant_mapping()
    color_mapping = mappings.create_color_mapping()
    category_mapping = mappings.create_category_mapping()
    allume_category_mapping = mappings.create_allume_category_mapping()
    size_mapping = mappings.create_size_mapping()
    shoe_size_mapping = mappings.create_shoe_size_mapping()
    size_term_mapping = mappings.create_size_term_mapping()

    network = mappings.get_network('CJ') # update this function to add the network

    destination = local_temp_dir + '/cleaned/cj_flat_file.csv'

    with open(destination, "w") as cleaned:
        file_list = []
        file_directory = os.listdir(local_temp_dir)

        for f in file_directory:
            if f.endswith('.txt'):
                # file_list.append(os.path.join(os.getcwd(), local_temp_dir, f))
                file_list.append(f)

        # metric variables
        totalCount = 0
        writtenCount = 0
        genderSkipped = 0
        categoriesSkipped = 0
        merchantCount = Merchant.objects.count()
        categoryCount = CategoryMap.objects.count()

        csv.register_dialect('reading', delimiter='\t', quoting=csv.QUOTE_NONE, quotechar='')
        csv.register_dialect('writing', delimiter=',', quoting=csv.QUOTE_ALL, quotechar='"', doublequote=False, escapechar='\\', lineterminator='\n')

        cleaned_fieldnames = cleaned_fields.split(',')
        writer = csv.DictWriter(cleaned, cleaned_fieldnames, dialect = 'writing')

        for f in file_list:
            # might need to do some merchant name stuff here
            full_filepath = os.path.join(os.getcwd(), local_temp_dir, f)
            with open(full_filepath, "r") as data:
                lines = data.readlines()

                # merchant_is_active = mappings.is_merchant_active(merchant_id, merchant_name, network, merchant_mapping)
                merchant_is_active = 1
                if merchant_is_active:
                    # omit fieldnames arg to use headerlines
                    reader = csv.DictReader(lines, restval = '', dialect = 'reading')

                    tempCount = 0
                    for datum in reader:
                        totalCount += 1
                        tempCount += 1

                        # unicode
                        for key, value in datum.iteritems():
                            datum[key] = value.decode('UTF-8')
                        
                        # temporary examining of datum (remove eventually)
                        # print '========================== Examining product %s ================================' % tempCount
                        # for key, value in datum.iteritems():
                        #     print (key, value)
                        # print '========================== Finish product %s ================================' % tempCount

                        if tempCount > 10:
                            return
                        ### need to examine more files, but if the keys used actually change between merchants
                        ### then maybe need configuration files kind of like with RAN except probably more annoying?
                        ### thought dictionary of terms that we want (such as color) to the labels that the specific merchant uses
                        ## reminds me of my interview problem lol


                        # attempt to load this yaml file in
                        # i'll need to make this more general...
                        # need to find the filepath


                        # merchant name is the filename until the first dash (at least for all present examples)
                        pattern = re.compile('^[^-]*') # pattern matches until the first hyphen
                        match = re.search(pattern, f)
                        merchant_name = match.group(0) # match will be the entire filename in absence of a dash
                        merchant_id = product_feed_helpers.generate_merchant_id(merchant_name)

                        # because we need to generate the merchant id also, we need to name the configuration files
                        # after merchant name and search for them based on that
                        config_filename = merchant_name + '.yaml'
                        config_filepath = os.path.join(os.getcwd(), 'tasks/product_feed_py/merchants_config_cj', config_filename)
                        config_file = open(config_filepath, "r")
                        with open(config_filepath, "r") as config_file:
                            y = yaml.load(config_file)
                            mapping_dict = y['fields']


                        # no gender skipping because no gender information?

                        # if i see any instances of it, need to handle how to try and unpack values that exist for some merchants but not for others

                        # first way is to go key by key and retrieve from dictionary, but there is proooobably a faster method to do so
                        # unpack the keys
                        merchant_color_key = mapping_dict['merchant_color']
                        size_key = mapping_dict['size']
                        primary_category_key = mapping_dict['primary_category']
                        product_name_key = mapping_dict['product_name']


                        secondary_category_key = mapping_dict['secondary_category']

                        # add a null mapping to each data point
                        datum['N/A'] = ''
                        print '========================== Examining product %s ================================' % tempCount
                        for key, value in datum.iteritems():
                            print (key, value)
                        print '========================== Finish product %s ================================' % tempCount

                        primary_category = datum[primary_category_key]
                        secondary_category = ''

                        allume_category = mappings.are_categories_active(primary_category, secondary_category, category_mapping, allume_category_mapping, merchant_name)
                        allume_category = 'allume_category'
                        if allume_category:
                            record = {}

                            merchant_color = datum[merchant_color_key]
                            record['merchant_color'] = merchant_color
                            merchant_color = merchant_color.lower()
                            try:
                                allume_color = color_mapping[merchant_color]
                            except:
                                allume_color = u'other'
                            record['color'] = allume_color

                            product_name = datum[product_name_key]
                            record['product_name'] = product_name

                            # how do we handle blanks or unmappeds...
                            # record['age'] = datum[age_key]

                            size = datum[size_key].upper()
                            size = size.replace('~', ',')
                            record['size'] = size
                            record['allume_size'] = product_feed_helpers.determine_allume_size(allume_category, size, size_mapping, shoe_size_mapping, size_term_mapping)

                            record['product_id'] = product_feed_helpers.generate_product_id(product_name, size, merchant_color)
                            record['merchant_id'] = merchant_id

                            record['buy_url'] = u'' # buy_url is derived with no derivation method?
                            # record['raw_product_url'] = # derived



                            # ultimately we need these fields for every record
                            # - product_id
                            # - merchant_id
                            # - product_name
                            # - long_product_description
                            # - short_product_description
                            # - product_url
                            # - raw_product_url
                            # - product_image_url
                            # - buy_url
                            # - manufacturer_name
                            # - manufacturer_part_number
                            # - SKU
                            # - product_type
                            # - discount
                            # - discount_type
                            # - sale_price
                            # - retail_price
                            # - shipping_price
                            # - color
                            # - merchant_color
                            # - gender
                            # - style
                            # - size
                            # - allume_size
                            # - material
                            # - age
                            # - currency
                            # - availability
                            # - keywords
                            # - primary_category
                            # - secondary_category
                            # - allume_category
                            # - brand
                            # - updated_at
                            # - merchant_name
                            # - is_best_seller
                            # - is_trending
                            # - allume_score
                            # - current_price
                            # - is_deleted

                            # finish unicode sandwich
                            for key, value in record.iteritems():
                                record[key] = value.encode('UTF-8')

                            # size splitting stuff
                            parent_attributes = copy(record)
                            # TO-DO finish size splitting stuff

                            # write the record
                            writer.writerow(record)
                            writtenCount += 1


                        # merchant_color = datum[key_that_represents_merchant_color]

                        # some fields might be missing
                        # may need to generate product_id and merchant_id

                        # print merchant_color

                        # return





# I know that we want an attribute color (in a general sense)
# from the data
# however, we know that the data sources on CJ do not agree what to call color
# so, we have a translation dictionary, read from a yaml file, that maps these terms
# such that 'color': 'label' (where 'label' is the term the merchant stores color at)\
# so, we index into this dictionary and, using the specific configuration file for each merchant,
# set key_that_represents_color = mapping_dict['color'] # should map to the string 'label'
# then when we read in the data, we access color via datum[key_that_represents_color]

