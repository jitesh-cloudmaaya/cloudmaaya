from . import mappings, product_feed_helpers

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
        pass
