# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from product_feed_py.pepperjam import generate_product_id
from .product_feed_py.mappings import *
from product_feed_py.product_feed_helpers import *

# Create your tests here.
class GenerateProductIdTestCase(TestCase):
    """
    Simple tests to make sure attributes of the generated product id are within expectations.
    That is, ensure that the generated product_ids only consist of numeric characters, have a
    length no greater than 19, etc.
    """

    def test_generate_product_id(self):
        # both sku and merchant id are numeric
        self.assertEqual(u'82197041558', generate_product_id(u'821970', u'41558'))
        # sku contains alphabetic characters
        self.assertEqual(u'15164794137793', generate_product_id(u'OP47941', u'37793'))
        self.assertEqual(u'1911211696348333530', generate_product_id(u'sku169634833', u'35300'))
        # sku contains non alphanumeric characters
        self.assertEqual(u'2621268302324973024', generate_product_id(u'ZUZH-WX97-XS', u'41846'))
        # sku + merchant id is very long
        self.assertEqual(u'6592220150063020212', generate_product_id(u'65IVTO006-TUVMQU5HRSBHUkVZ0', u'38014'))

class ProductFeedHelpersTestCase(TestCase):
    """
    Tests the behavior of the methods used in product_feed_helpers.py. Useful for determining the behavior
    of the methods across network data feeds to ascertain whether the error is in the helper or the method
    of application. Furthermore, has uses in maintaining appropriate behavior of the functions even as 
    more requirements are illuminated.
    """

    def test_parse_raw_product_url(self):
        """
        Tests that the parse_raw_product_url function grabs the appropriate parameter.
        """
        ran_product_url0 = 'http://click.linksynergy.com/link?id=fRObjjh00YI&offerid=507227.11059255658&type=15&murl=https%3A%2F%2Fwww.thereformation.com%2Fproducts%2Fpoppy-dress-black'
        ran_product_url1 = 'http://click.linksynergy.com/link?id=fRObjjh00YI&offerid=396056.10149032802&type=15&murl=https%3A%2F%2Fwww.uniqlo.com%2Fus%2Fen%2Fws-hooded-jacket-134855COL15SMA005000.html%3Futm_source%3Dlinkshare%26utm_medium%3Dcse%26utm_term%3D134855-15-005-000'

        pepperjam_product_url0 = 'http://www.pjtra.com/t/Qz9JREdDP0NHSURESj9JREdD?url=https%3A%2F%2Fwww.nordstromrack.com%2Fshop%2Fproduct%2F1877489'

        impact_radius_product_url0 = 'http://dsw.pxf.io/c/380198/317666/4837?prodsku=58000000002119200010000Z0XLRG&u=https%3A%2F%2Fwww.dsw.com%2Fen%2Fus%2Fproduct%2Fhue-hosiery-opaque-tights%2F211920'

        # ran
        self.assertEqual('https://www.thereformation.com/products/poppy-dress-black', parse_raw_product_url(ran_product_url0, 'murl'))
        self.assertEqual('https://www.uniqlo.com/us/en/ws-hooded-jacket-134855COL15SMA005000.html?utm_term=134855-15-005-000', parse_raw_product_url(ran_product_url1, 'murl'))
        # pepperjam
        self.assertEqual('https://www.nordstromrack.com/shop/product/1877489', parse_raw_product_url(pepperjam_product_url0, 'url'))
        # impact_radius
        self.assertEqual('https://www.dsw.com/en/us/product/hue-hosiery-opaque-tights/211920', parse_raw_product_url(impact_radius_product_url0, 'u'))


# class MappingsTestCase(TestCase):
#     """
#     Some simple tests to confirm that mappings return a structure like we expect.
#     Changes like changes to the database table names should not break the mappings helpers,
#     these tests should quickly confirm basic sanity.
#     """

#     fixtures = ['MappingsTestCase']

#     def test_merchant_mapping(self):
#         """
#         Tests that a call to create_merchant_mapping creates a dictionary with the
#         expected structure: {long merchant_id: int active}
#         """
#         merchant_mapping = create_merchant_mapping()
#         self.assertIsNotNone(merchant_mapping)
#         # print merchant_mapping

#         # general structure
#         self.assertTrue(isinstance(merchant_mapping.keys()[0], long))
#         self.assertTrue(isinstance(merchant_mapping.values()[0], int))

#         # fixture specific
#         # self.assertEqual(1, merchant_mapping.keys()[0])

#     def test_color_mapping(self):
#         """
#         Tests that a call to create_color_mapping creates a dictionary with the
#         expected structure: {str external_color: str allume_color}
#         """
#         color_mapping = create_color_mapping()
#         self.assertIsNotNone(color_mapping)

#         # general structure
#         self.assertTrue(isinstance(color_mapping.keys()[0], unicode))
#         self.assertTrue(isinstance(color_mapping.values()[0], unicode))

#         # fixture specific
#         self.assertEqual(u'brown', color_mapping[color_mapping.keys()[0]])

#     def test_category_mapping(self):
#         """
#         Tests that a call to create_category_mapping create a dictionary with the
#         expected structure: {(str primary_category, str secondary_category):
#         (int allume_category_id, int active)}
#         """
#         category_mapping = create_category_mapping()
#         self.assertIsNotNone(category_mapping)

#         # general structure
#         k = category_mapping.keys()[0]
#         v = category_mapping.values()[0]
#         self.assertTrue(isinstance(k, tuple))
#         self.assertTrue(isinstance(k[0], unicode))
#         self.assertTrue(isinstance(k[1], unicode))
#         self.assertTrue(isinstance(v, tuple))
#         self.assertTrue(isinstance(v[0], long))
#         self.assertTrue(isinstance(v[1], int))

#         # fixture specific
#         info = category_mapping[k]
#         self.assertEqual(1, info[0])
#         self.assertEqual(1, info[1])

#     def test_allume_category_mapping(self):
#         """
#         Tests that a call to create_category_mapping creates a dictionary with the
#         expected structure: {long id: (unicode name, int active)}
#         """
#         allume_category_mapping = create_allume_category_mapping()
#         self.assertIsNotNone(allume_category_mapping)

#         # general structure
#         self.assertTrue(isinstance(allume_category_mapping.keys()[0], long))
#         v = allume_category_mapping.values()[0]
#         self.assertTrue(isinstance(v, tuple))
#         self.assertTrue(isinstance(v[0], unicode))
#         self.assertTrue(isinstance(v[1], int))

#         # fixture specific
#         info = allume_category_mapping[allume_category_mapping.keys()[0]]
#         self.assertEqual(u'Test Allume Category', info[0])
#         self.assertEqual(1, info[1])
#  
