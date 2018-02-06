import urlparse
import urllib

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
