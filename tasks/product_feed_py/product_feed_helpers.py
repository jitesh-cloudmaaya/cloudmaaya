import urlparse
import urllib
import hashlib
import re

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

    converted = int(hashlib.sha256(size).hexdigest(), 16) % (10 ** 15)
    product_id = int(product_id) + converted
    product_id = product_id % (2 ** 60) # keep id under bigint max signed value
    product_id = str(product_id)

    return product_id

def seperate_sizes(sizes):
    """
    Takes in a size attribute, intended to be from a product which has a comma seperated list as a size,
    and returns an array of individual size values to be used in creation of children records.
    Args:
      sizes (str): A string containing a comma seperated list of sizes of the product.

    Returns:
      arr: An array of the individual sizes.
    """
    arr = re.split(r'[,]+', sizes)
    for i in range(0, len(arr)):
      arr[i] = arr[i].strip()
    return arr

def determine_allume_size(allume_category, size, size_mapping, shoe_size_mapping, size_term_mapping):
    """


    Args:
      allume_category (str): The allume_category from the product. Should contain a value in the
      product_api_allumecategory table.
      size (str): The size the merchant provided, unless delimited.
      size_mapping (dict):
      shoe_size_mapping (dict):
      size_term_mapping (dict):

    Returns:
      str: The calculated allume_size to use.
    """
    if allume_category == 'Shoes':
        return _determine_allume_size_shoe(size, shoe_size_mapping, size_term_mapping)
    else:
        return _determine_allume_size(size, size_mapping, size_term_mapping)

def _determine_allume_size(size, size_mapping, size_term_mapping):
    """
    Takes in 

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

    # if the parsed size is only alphabetic characters and the dash character, check it against the size mapping
    # e.g., attempt to use X-LARGE -> XL
    # maybe look for anything but a number?

    # if it startswith a number
    try:
        starts_with_num = parsed_size[0].isdigit()
    except IndexError:
        starts_with_num = False


    # if alpha is only characters that occur in bra sizes? we know not to do the allume_size logic, it would 
    # likely need to be a bra size? [abcdefg] known
    # bool(re.match('^[abcdefgh]+$', s))
    # v2
    # not bool(re.compile(r'[^abcedfgh]').search(s)) # does not work for '' (would return True, when we prob want False)

    if starts_with_num:
        # check for the special cases of 1X, 2X, 3X, 4X
        special_cases = set(['0X', '1X', '2X', '3X', '4X'])
        if parsed_size in special_cases:
            allume_size = size_mapping[parsed_size]
        else:
            join_val = ''
            # check number split from characters?
            numeric, alpha = _split_size(parsed_size)
            if _lingerie_match(alpha): # we believe this to be lingerie
                allume_size = numeric + alpha
            else:
                if numeric in size_mapping.keys():
                    numeric = size_mapping[numeric]
                if alpha in size_term_mapping.keys():
                    alpha = size_term_mapping[alpha]
                    join_val = ' '
                allume_size = numeric + join_val + alpha
                allume_size = allume_size.strip()
    else:
        # DO MORE work here
        # check if it is a character size?
        if parsed_size in size_mapping.keys():
            allume_size = size_mapping[parsed_size]
        else:
            allume_size = parsed_size


    return allume_size


# mostly considered necessary because lingerie sizes occur when the allume_category is 'Other'
def _lingerie_match(characters):
    if len(characters) == 0:
        return False
    return not bool(re.compile(r'[^abcedfghABCDEFGH]').search(characters))

def _determine_allume_size_shoe(size, shoe_size_mapping, size_term_mapping):
    """
    

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

    join_val = ''
    # check if the seperated numeric value exists in the shoe size mapping
    if numeric in shoe_size_mapping.keys():
        numeric = shoe_size_mapping[numeric]
    if alpha in size_term_mapping.keys():
        # then attempt to expand the character part of the parsed size (there is also additional logic surrounding plus to be implemented here)
        alpha = size_term_mapping[alpha]
        join_val = ' '



    # then concatenate these values in some form or fashion (perhaps with only 1 space? or a space determined by whether or not there was a dict hit)
    allume_size = numeric + join_val + alpha
    allume_size = allume_size.strip()
    return allume_size

def _split_size(size): # maybe just for shoes???
    """
    Attempts to parse size such that a shoe size '7WW' seperates into the parts: '7' and 'WW'.

    Returns:
      tup:
    """
    match = re.compile("[^\W\d]").search(size)
    try:
        numeric = size[:match.start()].strip()
        alpha = size[match.start():].strip()
    except AttributeError: # match is None
        numeric = size
        alpha = ''
    return (numeric, alpha)

