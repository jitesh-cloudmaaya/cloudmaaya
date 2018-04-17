import urlparse
import urllib
import hashlib
import re
import unicodedata
from datetime import datetime, timedelta
from product_api.models import Merchant, CategoryMap, Network, Product, SynonymCategoryMap
from string import capwords

def parse_raw_product_url(product_url, raw_product_attribute):
    """
    Takes in the product_url of a product record and parses the raw_product_url to use for the record.
    Does an initial pass to access the query param corresponding to the raw_product_url. A second pass
    is performed to drop certain parameters from the url before finalizing it.

    Args:
      product_url (str): A string denoting the full product_url of the record.
      raw_product_attribute (str): A string denoting the dictionary field name to use in the first pass of the product_url.

    Returns:
      str: The raw_product_url to use for the record.
    """
    # pass one
    raw_product_url = urlparse.parse_qs(urlparse.urlsplit(product_url).query)[raw_product_attribute][0]

    # pass two
    # split the url into parts
    split = urlparse.urlsplit(raw_product_url)
    # parse the query parameters
    params = urlparse.parse_qs(urlparse.urlsplit(raw_product_url).query)  
    # drop the indicated query parameters (utm_medium, utm_source, utm_campaign, siteID)
    params.pop('utm_medium', None)
    params.pop('utm_source', None)
    params.pop('utm_campaign', None)
    params.pop('utm_content', None)
    params.pop('siteID', None)
    # reconstruct the params into useful query string
    query = urllib.urlencode(params, doseq=True)
    # replace the initial query value
    split = split._replace(query = query)
    # rejoin the split raw_product_url
    joined = urlparse.urlunsplit(split)

    return joined

# some notes on generate_product_id usage
# be very careful about which fields are used when generating the product id
# for example, to preserve the final count of products, use the merchant_color instead of the allume
# color and probably the merchant_size instead of the allume size (even if the products are then functionally identical)

def generate_product_id(product_name, merchant_size, merchant_color, SKU):
    """
    In the event that a product_id cannot be found, deterministically generate a product_id
    using that product's product_name, size, and color.

    Args:
      product_name (str): The product's name. Expects a unicode string.
      merchant_size (str): The merchant provided size field for the product. Expects a unicode string.
      merchant_color (str): The merchant provided color field for the product. Expects a unicode string.
      SKU (str): The SKU of the product. Expacts a unicode string.

    Returns:
      str: A string to use as the product's product_id.
    """
    step1 = int(hashlib.sha256(product_name.encode('UTF-8')).hexdigest(), 16) % (10 ** 15)
    step2 = int(hashlib.sha256(merchant_size.encode('UTF-8')).hexdigest(), 16) % (10 ** 15)
    step3 = int(hashlib.sha256(merchant_color.encode('UTF-8')).hexdigest(), 16) % (10 ** 15)
    step4 = int(hashlib.sha256(SKU.encode('UTF-8')).hexdigest(), 16) % (10 ** 15)

    product_id = step1 + step2 + step3 + step4
    product_id = product_id % (2 ** 60) # keep within mysql bigint
    product_id = str(product_id).decode('UTF-8')

    return product_id

def assign_product_id_size(product_id, size):
    """
    This helper function is used for deaggregating product records based on size. It generates
    a product_id to be used based on the size given and the product_id of the parent record.
    Args:
      product_id (str): The product_id of the parent record containing the list of sizes.
      size (str): One size from a seperated list of the product's sizes.

    Returns:
      str: The product_id to use in the associated child record.
    """

    converted = int(hashlib.sha256(size.encode('UTF-8')).hexdigest(), 16) % (10 ** 15)
    product_id = int(product_id) + converted
    product_id = product_id % (2 ** 60) # keep id under bigint max signed value
    product_id = str(product_id).decode('UTF-8')

    return product_id

def seperate_sizes(sizes):
    """
    Takes in sizes and determines if it can use any of the available parsing methods to seperate the 
    sizes into a distinct sizes array. Enforces a delimiter hierarchy of commas, hyphens. If the sizes
    passed in do not contain any of the delimiters, it returns the sizes attribute unchanged.
    Args:
      sizes (str): A string representing the size attribute of a product record.
    Returns:
      arr: An array of individual sizes.
    """
    if ',' in sizes:
        sizes = _comma_seperate_sizes(sizes)
    elif '/' in sizes:
        pass # no understanding yet of separation on slashes
        sizes = [sizes]
    elif '-' in sizes:
        sizes = _hyphen_seperate_sizes(sizes)
    else: # or size contains no sought delmiters
        sizes = [sizes]
    return sizes

def _comma_seperate_sizes(sizes):
    """
    Takes in a size attribute, intended to be from a product which has a comma seperated list as a size,
    and returns an array of individual size values to be used in creation of children records. If the sizes
    passed in do not contain a comma delimiter or is an otherwise malformed input, returns sizes as the single
    member of an array.
    Args:
      sizes (str): A string containing a comma seperated list of sizes of the product.

    Returns:
      arr: An array of the individual sizes.
    """
    arr = re.split(r'[,]+', sizes)
    for i in range(0, len(arr)):
      arr[i] = arr[i].strip()
    arr = filter(bool, arr)
    return arr
  
def _hyphen_seperate_sizes(sizes):
    """
    Takes in a size attribute, intended t obe from a product which has a hyphen seperated list as a size,
    and returns an array of individual size values to be used in the creation of children records. If the sizes
    passed in do not contain a hyphen delimiter or is an otherwise malformed input, returns sizes as the single
    member of an array.

    Args:
      sizes (str): A string representing the a character delimited list of sizes.

    Returns:
      arr: An array containing each distinct size from the input.
    """
    try:
        splitSizes = []
        # initialize a pointer to start of sizes string
        pointer = 0
        # start initialized to 0
        start = 0
        # end initialized to 0
        end = 0

        # iterate in this fashion until pointer > len(string)
        while (pointer < len(sizes)):
          # increment pointer and read character by character until/if we encounter whitespace
            if sizes[pointer] == '(': # search for a opening parentheses...
                # proceed to iterate until or if we reach a closure
                while sizes[pointer] != ')':
                    pointer += 1

            if sizes[pointer].isspace(): # we have encountered whitespace
                # if this happens, set end to pointer
                end = pointer
                # add the split size
                # then, keep reading until character is neither whitespace or a dash (increment the pointer)
                # while sizes[pointer].isspace() or sizes[pointer] == '-':
                  # pointer += 1
                while sizes[pointer].isspace():
                    pointer += 1
                # we should have the non whitespace char at pointer
                if sizes[pointer] == '-': # we found what we're looking for
                    while sizes[pointer].isspace() or sizes[pointer] == '-':
                        pointer += 1
                    splitSizes.append(sizes[start:end]) # off by one?
                    # the pointer value that occurs here is the new start
                    start = pointer
                elif sizes[pointer] == '(':
                    # proceed to iterate until or if we reach a closure
                    while sizes[pointer] != ')':
                        pointer += 1
            else:
              # repeat this process until we break out of the looping condition
                pointer += 1

        # then, append sizes[start:len(sizes)]
        splitSizes.append(sizes[start:len(sizes)])

        return splitSizes
    except IndexError as e:
        return [sizes]

def determine_allume_size(allume_category, size, size_mapping, shoe_size_mapping, size_term_mapping):
    """
    Takes in an allume_category and size and uses the relevant size mappings to determine an allume
    size to use. Method calls one of two helper methods for the logic to determine allume size.

    Args:
      allume_category (str): The allume_category from the product. Should contain a value in the
      product_api_allumecategory table.
      size (str): The size the merchant provided, unless delimited.
      size_mapping (dict): A dictionary created by the helper function. Uses the sizemap model.
      shoe_size_mapping (dict): A dictionary created by the helper function. Uses the shoesizemap model.
      size_term_mapping (dict): A dictionary created by the helper function. Uses the sizetermmap model.

    Returns:
      str: The calculated allume_size to use.
    """
    if allume_category == 'Shoes':
        return _determine_allume_size_shoe(size, shoe_size_mapping, size_term_mapping)
    else:
        return _determine_allume_size(size, size_mapping, size_term_mapping)

def _determine_allume_size(size, size_mapping, size_term_mapping):
    """
    Takes in a size and the relevant size mappings and determines the appropriate allume size using
    translation models. Additionally, expands certain key phrases into attributes of interest such as
    'Plus' or 'Petite'.

    Args:
      size (str): The string representing the distinct (not a list) size value of a product.
      size_mapping (dict): A dictionary created by the helper function. Uses the sizemap model.
      size_term_mapping (dict): A dictionary created by the helper function. Uses the sizetermmap model.

    Returns:
      str: The allume size to use. Can return the size that was passed in if there are no mapping hits.

    """
    # seperate the string from any part of the string that is contained in parentheses
    pattern = re.compile('^[^\(]+')
    match = re.match(pattern, size)
    try:
        parsed_size = match.group(0).strip()
    except AttributeError: # if match is None
        parsed_size = size

    # print '========= test sep =========='
    # print type(parsed_size)
    # print parsed_size

    # if it startswith a number
    try:
        starts_with_num = parsed_size[0].isdigit()
    except IndexError:
        starts_with_num = False

    if starts_with_num:
        # check for the special cases of 1X, 2X, 3X, 4X
        special_cases = set([u'0X', u'1X', u'2X', u'3X', u'4X'])
        if parsed_size in special_cases:
            # if size is 1X or above, it is plus
            special_cases.remove(u'0X')
            size_term = u''
            if parsed_size in special_cases:
                size_term = u'Plus'
            allume_size = size_mapping[parsed_size]
            if size_term:
                allume_size += u' ' + size_term
        else:
            join_val = u''
            # check number split from characters?
            numeric, alpha = _split_size(parsed_size)
            if _lingerie_match(alpha): # we believe this to be lingerie
                allume_size = numeric + alpha
            else:
                if numeric in size_mapping.keys():
                    numeric = size_mapping[numeric]
                if alpha in size_term_mapping.keys():
                    alpha = size_term_mapping[alpha]
                    join_val = u' '
                allume_size = numeric + join_val + alpha
                allume_size = allume_size.strip()

                # plus work?
                plus_sizes = [u'18', u'20', u'22', u'24', u'26']
                for plus_size in plus_sizes:
                    if plus_size in allume_size:
                        allume_size += u' Plus'
                        break
    else:
        # DO MORE work here
        # if it's a character size, and also xxl or xxxl, add plus?
        # check if it is a character size?
        if parsed_size in size_mapping.keys():
            allume_size = size_mapping[parsed_size]

            if u'XXL' in allume_size or u'XXXL' in allume_size:
                allume_size += u' Plus'
        else:
            allume_size = parsed_size
    # print 'allume size type is ' + str(type(allume_size))
    # print 'allume size is ' + allume_size
    # print 'parsed size type is ' + str(type(parsed_size))
    # print 'parsed size is ' + parsed_size

    # return allume_size.decode('UTF-8')
    return allume_size

def _determine_allume_size_shoe(size, shoe_size_mapping, size_term_mapping):
    """
    Takes in a size and the relevant size mappings and determines the appropriate allume size using
    translation models.

    Args:
      size (str): The string representing the distinct (not a list) size value of a product.
      size_mapping (dict): A dictionary created by the helper function. Uses the sizemap model.
      size_term_mapping (dict): A dictionary created by the helper function. Uses the sizetermmap model.

    Returns:
      str: The allume size to use. Can return the size that was passed in if there are no mapping hits.
    """
    # seperate the string from any part of the string that is contained in parentheses: 70 WW (US) -> 70 WW
    pattern = re.compile('^[^\(]+')
    match = re.match(pattern, size)
    try:
        parsed_size = match.group(0).strip()
    except AttributeError: # if match is None
        parsed_size = size

    # seperate this value into a numeric component and a character component (assumption is that shoe sizes start with numbers)
    # assuming that shoe sizes start with numbers, seperate the shoe size into a numeric and character component
    numeric, alpha = _split_size(parsed_size)

    join_val = u''
    # check if the seperated numeric value exists in the shoe size mapping
    if numeric in shoe_size_mapping.keys():
        numeric = shoe_size_mapping[numeric]
    if alpha in size_term_mapping.keys():
        # then attempt to expand the character part of the parsed size (there is also additional logic surrounding plus to be implemented here)
        alpha = size_term_mapping[alpha]
        join_val = u' '

    # then concatenate these values in some form or fashion (perhaps with only 1 space? or a space determined by whether or not there was a dict hit)
    allume_size = numeric + join_val + alpha
    allume_size = allume_size.strip()
    return allume_size

def _split_size(size):
    """
    Attempts to parse size values by finding the divider of where the first non-numeric character occurs.
    It splits the string at that point, determining everything before the partition to be a numeric component
    of the size and everything occuring after the partition is determined to be the alphabetical component.

    Args:
      size (str): The string representing the distinct (not a list) size value of a product.

    Returns:
      tup: Returns a two argument tuple where the first element is the numeric component of the
      size and the second element is the alphabetic component of the size.
    """
    match = re.compile("[^\W\d]").search(size)
    try:
        numeric = size[:match.start()].strip()
        alpha = size[match.start():].strip()
    except AttributeError: # match is None
        numeric = size
        alpha = u''
    return (numeric, alpha)

# mostly considered necessary because lingerie sizes occur when the allume_category is 'Other'
def _lingerie_match(characters):
    """
    Takes in a string of characters and determines if the characters consist only of the set of
    characters that are seen to compose bra sizes.

    Args:
      characters (str): A string of characters that compose the character component of a numeric
      and character size value.

    Returns:
      bool: Returns whether or not the set of characters consists of only valid bra size letters.
    """
    if len(characters) == 0:
        return False
    return not bool(re.compile(r'[^abcedfghABCDEFGH]').search(characters))

def set_deleted_network_products(network, threshold = 12):
    """
    Helper method for use in the main data feed method. Collects a list data feed products
    that should have been upserted in the current run. For those that were determined to not have
    been upserted, set those products to a status of is_deleted = True.

    Args:
      network (str): The network name. Should correspond to the network name used in the
      product_api_network table.
      threshold (int): The time threshold in hours. If the updated-at value of a record is threshold
      or more hours old, conclude that it was not updated in the current upsert and set to deleted.
    """
    network_id = Network.objects.get(name=network)
    merchants = Merchant.objects.filter(active=True, network_id=network_id)
    merchant_ids = merchants.values_list('external_merchant_id')
    products = Product.objects.filter(merchant_id__in = merchant_ids)
    datetime_threshold = datetime.now() - timedelta(hours = threshold)
    deleted_products = products.filter(updated_at__lte = datetime_threshold)
    updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #deleted_products.update(is_deleted = True, updated_at = updated_at)
    print('Set %s non-upserted products to deleted' % deleted_products.count())

def generate_merchant_id(merchant_name):
    """
    In the event of an absent merchant id from data, generate it using the merchant name.
    Necessary due to the need for a unique merchant id and product id pair as a unique index
    on the products table for the upsert process.

    Args:
      merchant_name (str): A string representing the name of the merchant.
    Returns:
      str: A string corresponding of purely numbers. Intended for use as a product's
      merchant id.
    """
    # value needs to fit in a mysql int because the values of merchant_id 
    # and external_merchant id do not match between the product_api_product
    # and product_api_merchant tables...
    converted = int(hashlib.sha256(merchant_name.encode('UTF-8')).hexdigest(), 16) % (10 ** 7) # the power to raise to has wiggle room
    merchant_id = str(converted).decode('UTF-8')
    return merchant_id

def parse_category_from_product_name(product_name, synonym_category_mapping):
    """
    Using SynonymCategoryMap, checks a product_name for presence of any synonyms. If one is found,
    leverages the SynonymCategoryMap objects to find the category that synonym should map to. This
    category is then returned.

    Args:
      product_name (str): The name of a product, with elements separated by an arbitrary amount
      of whitespace.

    Returns:
      str: The category that was parsed from a synonym appearing in the product name.
    """
    matched_synonym = None
    currIndex = -1
    synonyms_list = synonym_category_mapping.keys()
    product_name = product_name.lower()
    for synonym in synonyms_list:
        pattern = re.compile(r'\b' + synonym.lower() + r'\b')
        match = re.search(pattern, product_name)
        if match:
            index = match.end()
            if index > currIndex:
                currIndex = index
                matched_synonym = synonym

    category = u''
    if matched_synonym:
        category = synonym_category_mapping[matched_synonym]
    return category

def product_field_tiered_assignment(tiered_assignments, product_fieldname, datum, default, **kwargs):
    """
    Attempts a best effort assignment of fieldname using tiered_assigments and the information encoded in datum.
    Uses the first field label from tiered_assignments that has a non-empty value. If a non-empty value cannot be
    resolved, the function returns an empty value.
    Example: _product_field_tiered_assignment({'primary_category': ['primary_category', 'attribute_2_product_type']},
        'primary_category', {'primary_category': '', 'attribute_2_product_type': 'Beauty & Fragrance'}) -> 'Beauty & Fragrance'

    Args:
      tiered_assignments (dict): A dictionary representing categories with tiered assignment possibilities.
      The dictionary has keys of strings that are fieldnames in the datum and the values are list of strings,
      with each string representing code that is a strategy to generate an assignment. The list is sequential.
      product_fieldname (str): A string denoting the fieldname label that is used as a key in datum.
      datum (dict): A dictionary representing the raw data from a RAN file. Maps field attribute labels to
      a string representing their value.
      default (str): The default string value to use for assignment in the event that the product fieldname
      has no tiered assignment defined in the network merchant's configuration file.

    Returns:
      str: The assignment that was found and used. Can be the empty string.
    """
    try:
        # see if the tiered_assignments dictionary has a list of strategies to try for populating this particular fieldname?
        strategy_list = tiered_assignments[product_fieldname]
        # if it does not, it will be a keyerror
    except KeyError:
        return default

    assignment = ''
    for strategy in strategy_list:
        assignment = eval(strategy)
        if assignment:
            break
    return assignment


# figure out what to do with _check_other_term_maps
def parse_other_terms(product_name):
    """
    Using SynonymCategoryMap objects with a category of 'Other', checks a product_name for the presence of
    any synonyms. If it finds one, it returns the word 'Other', intended to be used as the category for a
    product. If it does not find any terms, it returns the empty string.

    Args:
      product_name (str): The name of a product, with elements separated by an arbitrary amount
      of whitespace.

    Returns:
      str: Returns one of two strings; either the string 'Other' or the empty string ''.
    """
    synonym_other_terms = SynonymCategoryMap.objects.filter(category = 'Other').values_list('synonym', flat=True)
    product_name = product_name.lower()
    for term in synonym_other_terms:
        term = term.lower()
        if term in product_name:
            return u'Other'

    return u''

def normalize_data(text, form='NFD'):
    """
    Necessary to fit potential unicode data to MySQL tables with latin1 charsets.
    """
    try:
        text = unicode(text, 'utf-8')
    except (TypeError, NameError):
        pass
    text = unicodedata.normalize(form, text)
    text = text.encode('ascii', 'ignore')
    text = text.decode('utf-8')
    return text
