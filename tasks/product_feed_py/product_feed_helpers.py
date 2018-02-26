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
