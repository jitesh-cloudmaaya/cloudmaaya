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

def determine_allume_size(allume_category, size, size_mapping, shoe_size_mapping):
    """


    Args:
      allume_category (str): The allume_category from the product. Should contain a value in the
      product_api_allumecategory table.
      size (str): The size the merchant provided, unless delimited.
      size_mapping (dict):
      shoe_size_mapping (dict):

    Returns:
      str: The calculated allume_size to use.
    """
    if allume_category == 'Shoes':
        return _determine_allume_size_shoe(size, shoe_size_mapping)
    else:
        return _determine_allume_size(size, size_mapping)

def _determine_allume_size(size, size_mapping):
    """
    aaaaaa

    Args:
      size (str):
      size_mapping (dict):

    Returns:
      str: 

    """
    if size in size_mapping.keys():
        allume_size = size_mapping[size]
    else:
        allume_size = size
    return allume_size

def _determine_allume_shoe_size2(size, shoe_size_mapping):
    """
    """
    # seperate the string from any part of the string that is contained in parentheses: 70 WW (US) -> 70 WW
    pattern = re.compile('^[^\(]+')
    match = re.match(pattern, size)
    try:
        parsed_size = match.group(0).strip()
    except AttributeError: # if match is None
        # do something
        pass

    # seperate this value into a numeric component and a character component (assumption is that shoe sizes start with numbers)
    # assuming that shoe sizes start with numbers, seperate the shoe size into a numeric and character component
    
    

# strategy for shoe size mapping
# check if the seperated numeric value exists in the shoe size mapping
    # if yes, use that value, if no keep the same
# then attempt to expand the character part of the parsed size (there is also additional logic surrounding plus to be implemented here)
    # if yes, use that value, if no keep the same (WW -> WIDE but D -> D)
# then concatenate these values in some form or fashion (perhaps with only 1 space? or a space determined by whether or not there was a dict hit)


def _determine_allume_size_shoe(size, shoe_size_mapping):
    """
    aaaaaaa

    Args:
      size (str):
      size_mapping (dict):

    Returns:
      str:
    """
    if size in shoe_size_mapping.keys():
        allume_size = shoe_size_mapping[size]
    else:
        allume_size = size
    return allume_size







    
