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
    This helper function is used in deaggregating product records based on size. It generates
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

#####################################################################################################################################
#####   BEGIN OLD SIZE PARSING LOGIC
#####################################################################################################################################

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

#####################################################################################################################################
#####   END OLD SIZE PARSING LOGIC
#####################################################################################################################################

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

def parse_category_from_product_name(product_name, synonym_category_mapping, exclusion_terms):
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
    # first check for any exclusion terms
    for term in exclusion_terms:
        pattern = re.compile(r'\b' + term.lower() + r'\b')
        match = re.search(pattern, product_name)
        if match:
            return 'Exclude'
    # then check for any synoynm terms, while prioritizing 'other'
    for synonym in synonyms_list:
        pattern = re.compile(r'\b' + synonym.lower() + r'\b')
        match = re.search(pattern, product_name)
        if match:
            index = match.end()

            # presence of 'Other' term overrides all alternative category choices
            category = synonym_category_mapping[synonym]
            if category == u'Other':
                return category

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
def parse_other_terms(product_name, synonym_other_category_mapping):
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
    product_name = product_name.lower()
    for term in synonym_other_category_mapping:
        term = term.lower()
        if term in product_name:
            return u'Other'

    return u''

#####################################################################################################################################
#####   BEGIN NEW SIZE PARSING LOGIC
#####################################################################################################################################

import logging

logger = logging.getLogger(__name__)


def parse_single_size(v, product_name, allume_category, known_text_sizes, known_number_sizes):
    # statics
    known_separators = ['/']
    inseam_sizes = ['TALL'] #
    eu_can_obj_sizes = {'EU': 'EU', 'DE': 'DE', 'IT': 'IT', 'FR': 'FR', 'CAN': 'CAN', 'US': 'US'}
    non_eu_us_sizes = ['UK', 'AUS']
    non_eu_us_sizes_obj = {'UK': 'UK', 'AUS': 'AUS'}

    is_shoe_size = allume_category == 'SHOES'
    name_in_caps = product_name.upper()
    v = v.upper()
    if re.compile(r"^TALL").match(name_in_caps) and not re.compile(r"(LONG|TALL|W|E)+").match(v):
        v = 'TALL ' + v
    if re.compile(r"^PETITE").match(name_in_caps) and not re.compile(r"(SHORT|P|N|A|PETITE)+").match(v):
        v = 'PETITE ' + v
    saved_parsed_data = v
    parsed_v = saved_parsed_data
    res = []
    if 'MONTHS' in parsed_v or 'AGE' in parsed_v or 'NEWBORN' in parsed_v or 'CHILD' in parsed_v or 'TODDLER' in parsed_v or 'BABY' in parsed_v or 'MTHS' in parsed_v:
        res.append(parsed_v)
        # return {'error': res} # no way of handling this as of current
        print str(res)
        print 'this size should not appear in the data ultimately... to-do...'
        return res

    text_sizes = known_text_sizes.copy()
    text_sizes.update(known_number_sizes)
    while parsed_v:
        saved_parsed_data = clean_up_data(parsed_v, is_shoe_size, known_text_sizes, eu_can_obj_sizes, non_eu_us_sizes_obj)
        parsed_v = re.sub(r"^(US|FR|EU|DE|IT|CAN)\s*", '', saved_parsed_data)
        parsed_v = re.sub(r"\s+(US|FR|EU|DE|IT|CAN)\s*", '', parsed_v)
        if re.compile(r"^(\.|[0-9])+(US|FR|EU|DE|IT|CAN)$").match(parsed_v):
            parsed_v = re.sub(r"(US|FR|EU|DE|IT|CAN)", '', parsed_v)
        single_size_with_country_indicator_and_inseam_removed = re.sub(r"^(UK|AUS|TALL)\s*", '',
                                                                       parsed_v)
        single_size_with_country_indicator_and_inseam_removed = re.sub(r"\s+(UK|AUS|TALL)\s*", '',
                                                                       single_size_with_country_indicator_and_inseam_removed)
        if known_text_sizes.get(single_size_with_country_indicator_and_inseam_removed) or known_number_sizes.get(
                single_size_with_country_indicator_and_inseam_removed):
            is_non_eu_us = False
            has_inseam_sizes = False
            for i in non_eu_us_sizes:
                if i in parsed_v:
                    is_non_eu_us = True
                    for j in inseam_sizes:
                        if j in parsed_v:
                            has_inseam_sizes = True
                            res.append(
                                # known_number_sizes[
                                    j + ' ' + known_number_sizes[i + single_size_with_country_indicator_and_inseam_removed]
                                # ]
                             )
                            break
                    if not has_inseam_sizes:
                        res.append(known_number_sizes[i + single_size_with_country_indicator_and_inseam_removed])
                    break
            if not is_non_eu_us:
                for k in inseam_sizes:
                    if k in parsed_v:
                        has_inseam_sizes = True
                        res.append(
                            # known_number_sizes[
                                k + ' ' + text_sizes[single_size_with_country_indicator_and_inseam_removed]
                            # ]
                        )
                        break
                if not has_inseam_sizes:
                    res.append(text_sizes[single_size_with_country_indicator_and_inseam_removed])
            parsed_v = None
        else:
            size_separator = has_any(parsed_v, known_separators)
            if size_separator:
                splitted_sizes_with_known_text_sizes = get_splitted_sizes_with_known_text_number_sizes(parsed_v,size_separator,known_text_sizes,known_number_sizes)
                if splitted_sizes_with_known_text_sizes:
                    res = res + splitted_sizes_with_known_text_sizes
                    parsed_v = None
                else:
                    splitted_sizes_with_US_text = get_splitted_sizes_with_US_text(parsed_v, size_separator)
                    if splitted_sizes_with_US_text:
                        if parsed_v != splitted_sizes_with_US_text:
                            parsed_v = splitted_sizes_with_US_text
                        else:
                            # preventing infinite loop
                            parsed_v = None
                    else:
                        splitted_sizes_with_INT_text = get_splitted_sizes_with_EU_CAN_text(parsed_v, size_separator, eu_can_obj_sizes)
                        if splitted_sizes_with_INT_text:
                            if parsed_v != splitted_sizes_with_INT_text:
                                parsed_v = splitted_sizes_with_INT_text
                            else:
                                # preventing infinite loop
                                parsed_v = None
                        else:
                            parsed_v = None
            else:
                parsed_v = None
    return [saved_parsed_data] if len(res) == 0 else res

def get_splitted_sizes_with_known_text_number_sizes(val, separator, known_text_sizes, known_number_sizes):
    import re
    res = []
    allume_petite_sep = 'p-als-'
    val = re.sub(r'^P/', allume_petite_sep, val)
    sizes = val.split(separator)
    z = known_text_sizes.copy()
    z.update(known_number_sizes)
    for size in sizes:
        updated_size = size.replace(allume_petite_sep, 'P/').strip()
        if z.get(updated_size):
            res.append(updated_size)
    return res


def get_splitted_sizes_with_US_text(val, separator):
    import re
    res = []
    allume_petite_sep = 'p-als-'
    val = re.sub(r'^P/', allume_petite_sep, val)
    sizes = val.split(separator)
    for size in sizes:
        size = size.strip()
        if 'US' in size and 'AUS' not in size:
            res.append(re.sub(r'^US\s*|\s+US\s*', '', size))
    return separator.join(res).replace(allume_petite_sep, 'P/') if res else None


def get_splitted_sizes_with_EU_CAN_text(val, separator, eu_can_obj_sizes):
    import re
    res = []
    allume_petite_sep = 'p-als-'
    val = re.sub(r'^P/', allume_petite_sep, val)
    sizes = val.split(separator)
    for size in sizes:
        size = size.strip()
        for eu_can_obj_size in eu_can_obj_sizes:
            if eu_can_obj_size in size:
                res.append(re.sub(r'^'+eu_can_obj_size+'\s*|\s+'+eu_can_obj_size+'\s*', '', size))
    return separator.join(res).replace(allume_petite_sep, 'P/') if res else None


def has_any(val, entries):
    for entry in entries:
        if entry in val:
            return entry
    return None


def clean_up_data(val, is_shoe_size, known_text_sizes, eu_can_obj_sizes, non_eu_us_sizes_obj):
    import re
    val = re.sub(r"\s+", ' ', val)
    val = re.sub(r"\"+", '', val).upper().strip()
    if 'SHORT' in val:
        val = 'PETITE' + val.replace('SHORT', '')
    if 'LONG' in val:
        val = 'TALL' + val.replace('LONG', '')

    if re.compile(r"[0-9]+\s+1/2\s*").match(val):
        val = re.sub(r'\s*1/2', '.5', val)
    if "(" in val:
        val = re.sub(r"\(+", '(', val)
        val = re.sub(r"\)+", ')', val)
        open_idx = val.index('(')
        if ")" not in val:
            val = val + ')'
        close_idx = val.index(')')
        before_open = val[:open_idx].strip()
        within_parenthesis = val[open_idx+1:close_idx].strip()
        after_close = val[close_idx+1:].strip()
        out_of_parenthesis = before_open if before_open else after_close
        within_parenthesis_chars = re.sub(r'[^zA-Z]+', '', within_parenthesis)
        within_parenthesis_numbers = re.sub(r'[^0-9]+', '', within_parenthesis)
        out_of_parenthesis_chars = re.sub(r'[^A-Z]+', '', out_of_parenthesis)
        out_of_parenthesis_numbers = re.sub(r'[^0-9]+', '', out_of_parenthesis)
        if within_parenthesis and not out_of_parenthesis:
            val = within_parenthesis
        elif out_of_parenthesis and not within_parenthesis:
            val = out_of_parenthesis
        elif 'US' in within_parenthesis_chars and 'AUS' not in within_parenthesis_chars:
            val = within_parenthesis if within_parenthesis_numbers else out_of_parenthesis
        elif 'US' in out_of_parenthesis_chars and 'AUS' not in out_of_parenthesis_chars:
            val = out_of_parenthesis if out_of_parenthesis_numbers else within_parenthesis
        else:
            if re.compile(r"^[A-Z]+[-A-Z]*$").match(out_of_parenthesis) and within_parenthesis == 'P':  # "X-SMALL (P)"
                val = 'PETITE ' + val[: val.index(' ')]
            elif re.compile(r"^[0-9]+W$").match(out_of_parenthesis) and re.compile(r"^[A-Z-0-9]*$").match(within_parenthesis):
                val = out_of_parenthesis
            elif re.compile(r"^[A-Z]+/[A-Z]+$").match(out_of_parenthesis) and re.compile(r"^[A-Z0-9]+-[A-Z0-9]+$").match(within_parenthesis):
                val = out_of_parenthesis
            elif '-' in within_parenthesis:
                val = within_parenthesis
            elif '-' in out_of_parenthesis:
                val = out_of_parenthesis
            elif non_eu_us_sizes_obj.get(within_parenthesis):
                val = within_parenthesis + ' ' + out_of_parenthesis
            elif non_eu_us_sizes_obj.get(out_of_parenthesis):
                val = out_of_parenthesis + ' ' + within_parenthesis
            elif re.compile(r"^[0-9]+X$").match(out_of_parenthesis) and (re.compile(r"^[0-9]+[/|-][0-9]+").match(within_parenthesis) or re.compile(r"^[0-9]+").match(within_parenthesis)):
                val = within_parenthesis
            elif re.compile(r"^[0-9]+P$").match(out_of_parenthesis) and re.compile(r"^[0-9]+").match(within_parenthesis):
                val = within_parenthesis
            elif known_text_sizes.get(within_parenthesis):
                val = within_parenthesis
            elif known_text_sizes.get(out_of_parenthesis):
                val = out_of_parenthesis
            elif within_parenthesis_chars and out_of_parenthesis_chars:
                val = out_of_parenthesis if len(out_of_parenthesis_chars) > len(within_parenthesis_chars) else within_parenthesis
            elif within_parenthesis_chars:
                val = within_parenthesis
            elif out_of_parenthesis_chars:
                val = out_of_parenthesis
            else:
                if len(within_parenthesis_numbers) == len(within_parenthesis) and len(out_of_parenthesis_numbers) == len(out_of_parenthesis): #both numbers only
                    val = within_parenthesis if int(within_parenthesis_numbers) < int(out_of_parenthesis_numbers) else out_of_parenthesis
                elif len(within_parenthesis_numbers) == len(within_parenthesis) and len(out_of_parenthesis_numbers) != len(out_of_parenthesis):
                    val = out_of_parenthesis
                else:
                    val = within_parenthesis

    for c in eu_can_obj_sizes:
        if re.compile(r'\s+' + c + '|[0-9.]+\s*' + c + '|^[0-9.]+-' + c + '$').match(val):
            val = re.sub(r'-?'+c, '', val)
    if is_shoe_size:
        if re.compile(r"^MENS\s+[.0-9]+\s*/\s*WOMENS\s+[.0-9]+$").match(val):
            val = re.sub("WOMENS\s+", '', val[val.index('/')+1:]).strip()
        if re.compile(r"^[.0-9]+[B|C]/[.0-9]+[B|C]$").match(val):
            val = val.replace('B', '').replace('C', '')
        if re.compile(r"^[.0-9]+\s+WMN\s+/\s+[.0-9]+\s+MEN$").match(val):
            val = val[:val.index('WMN')].strip()
        if re.compile(r"^WOMENS\s+[.0-9]+\s+/\s+MENS\s+[.0-9]+$").match(val):
            val = re.sub("WOMENS\s+", '', val[:val.index('/')]).strip()
        if re.compile(r"^[0-9.]+\s+MEN\s+/\s+[0-9.]+\s+WOM$").match(val):
            val = re.sub("\s+WOM", '', val[val.index('/') + 1:]).strip()
        if re.compile(r"^[0-9]+[.0-9]*-[0-9]+[.0-9]*$").match(val):
            val = re.sub(r'-', '/', val)
        if re.compile(r"^[0-9]+.0/[0-9]+.0$").match(val):
            val = val.replace('.0', '')
        if 'WIDE' in val:
            val = 'SHOEWIDE' + val.replace('WIDE', '')
        if re.compile(r"[0-9.]*\s*[WE]+$").match(val) or re.compile(r"[0-9.]*\s*[WE]+\s+").match(val):
            val = 'SHOEWIDE' + re.sub(r'\s*W+\s*', '', val).strip()
        if re.compile(r"[0-9.]*\s*[NA]+$").match(val) or re.compile(r"[0-9.]*\s*[NA]+\s+").match(val):
            val = 'SHOENARROW' + re.sub(r'\s*[NA]+\s*', '', val).strip()
    else:
        if re.compile(r"^W[0-9]{4}").match(val) or re.compile(r"^[0-9]{4}").match(val) or re.compile(
                "^[0-9]{2}\s*X\s*[0-9]{1,2}").match(val):
            val = 'WAIST' + re.sub(r'[^0-9]+', '', val)[:2]
        if re.compile(r"^[0-9]\s*X\s*[0-9]{1,2}").match(val):
            val = 'WAIST' + re.sub(r'[^0-9]+', '', val)[:1]
        if re.compile(r"^[0-9]+X/[0-9]+\s*-\s*[0-9]+W?").match(val):
            has_w = 'W' in val
            val = ('WAIST' if has_w else '') + val[val.index('/') + 1:val.index('-')].strip() + '/' + ('WAIST' if has_w else '') + val[val.index('-') + 1:].strip().replace('W', '')
        if re.compile(r"^[0-9]+INCH$").match(val):
            val = 'WAIST' + val.replace('INCH', '')
        if re.compile(r"^[0-9]+W?[-|/][0-9]+\s*W?$").match(val):
            val = val.replace('-', '/').replace('W', '').strip()
        if re.compile(r"^[0-9]+\s*W\s+|^[0-9]+\s*W$").match(val):
            val = re.sub(r'\s*W\s*', '', val)
        if re.compile(r"^(PETITE|TALL)[0-9]+\s*W\s+|^(PETITE|TALL)[0-9]+\s*W$").match(val):
            val = re.sub(r'\s*W\s*', '', val)

    if re.compile(r"[0-9.]+\s*[BMR]+$").match(val) or re.compile(r"[0-9.]+\s*[BMR]+\s+").match(val):
        val = re.sub(r'[BMR]*', '', val).strip()
    if re.compile(r"^[0-9]+/[A-Z]+-*[A-Z]*").match(val):
        val = val[val.index('/') + 1:]
    if re.compile(r"^[a-z-A-Z]+:\s+[0-9]+-*[0-9]*").match(val):
        temp_val_char = re.sub(r'[^a-zA-Z]+', '', val)
        if known_text_sizes.get(temp_val_char):
            val = temp_val_char
        else:
            val = val[val.index(':') + 1:]
    if re.compile(r"^[0-9]+\s*M\s+|^[0-9]+\s*M$").match(val):
        val = re.sub(r'\s*M\s*', '', val).strip()
    if re.compile(r"^[a-zA-Z]+-[a-zA-Z]+$").match(val):
        temp_val = val.split('-')
        if known_text_sizes.get(temp_val[0]) and known_text_sizes.get(temp_val[1]):
            val = val.replace('-', '/')
    if re.compile(r"^[0-9]+/[0-9]+[p|P]$").match(val):
        val = val.replace('/', 'P/')
    if re.compile(r"^[0-9]+-[0-9]+[p|P]$").match(val):
        val = val.replace('-', 'P/')
    if re.compile(r"^P/[A-Z]+-[A-Z]+$").match(val):
        val = 'PETITE ' + val[val.index('/') + 1: val.index('-')] + '/PETITE ' + val[val.index('-') + 1:]
    if re.compile(r"^[A-Z]+/[A-Z]+\s*-\s*P$").match(val):
        val = 'PETITE ' + val[: val.index('/')] + '/PETITE ' + val[val.index('/') + 1:val.index(' ')]
    if re.compile(r"^PETITE\s+[A-Z]+\s+/\s+[A-Z]+$").match(val):
        val = 'PETITE ' + val[val.index(' ') + 1: val.index(' /')] + '/PETITE ' + val[val.index('/ ') + 1:]
    if re.compile(r"^PETITE\s*/\s*[0-9]+\s*-\s*[0-9]+$").match(val):
        val = ('PETITE ' + val[val.index('/') + 1: val.index('')]).strip() + (
        '/PETITE ' + val[val.index('-') + 1:]).strip()
    if re.compile(r"^PETITE[0-9]+-[0-9]+$").match(val):
        val = ('PETITE ' + val[:val.index('-')].replace('PETITE', '')).strip() + (
        '/PETITE ' + val[val.index('-') + 1:]).strip()
    if re.compile(r"^PETITE\s+[0-9]+\s+-\s+[0-9]+L$").match(val):
        val = (val[:val.index('-')]).strip()
    if re.compile(r"^[A-Z]+-?[A-Z]*\s*[0-9]+([-|/][0-9]+)?$").match(val):
        temp_val = re.sub(r'[^A-Z]+', '', val)
        if known_text_sizes.get(temp_val) and 'P' not in temp_val:
            val = temp_val
    if re.compile(r"^[0-9]+\s*[A-Z]+[-A-Z]*$").match(val):
        temp_val = re.sub(r'[^A-Z]+', '', val)
        if known_text_sizes.get(temp_val) and 'P' not in temp_val:
            val = temp_val
    if re.compile(r"^P[A-Z]\s+[0-9]+P$").match(val):
        val = (val[val.index(' '):]).strip()
    if re.compile(r"^SIZE\s*[0-9]+$").match(val):
        val = re.sub(r'^SIZE\s*', '', val).strip()
    if re.compile(r"^SZ\s*[0-9]+\s+TALL$").match(val):
        val = 'TALL' + re.sub(r'[^0-9]+', '', val)
    if re.compile(r"^[0-9]+UK$").match(val):
        val = 'UK' + re.sub(r'[^0-9]+', '', val)
    if re.compile(r"^[.0-9]+-[.0-9]+$").match(val):
        val = val.replace('-', '/')
    if re.compile(r"^[.0-9]+S+$").match(val):
        val = 'PETITE ' + val.replace('S', '')
    if 'XSS' == val:
        val = 'XS/S'

    if re.compile(r"^[.0-9]+-[.0-9]+$").match(val):
        val = val.replace('-', '/')


    val = re.sub(r"EXTRA", 'X', val)
    val = re.sub(r"REGULAR|REG|UNISEX", '', val)
    val = re.sub(r"\s+", ' ', val).strip()
    return val


#####################################################################################################################################
#####   END NEW SIZE PARSING LOGIC
#####################################################################################################################################

def unicode_encode(value):
    """
    try to handle unicode errors more smoothly
    """
    try:
        return value.encode('UTF-8')
    except UnicodeDecodeError:
        return value
