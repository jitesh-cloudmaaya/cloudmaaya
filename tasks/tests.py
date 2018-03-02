# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from product_feed_py.pepperjam import generate_product_id
from .product_feed_py.mappings import *
from product_feed_py.product_feed_helpers import *
from product_feed_py.product_feed_helpers import _hyphen_seperate_sizes, _comma_seperate_sizes

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

class ParserTestCase(TestCase):
    """
    Tests the behavior and ability of seperating sizes based on a pre-decided list of 
    delimiters. Tests both the smaller private methods that seperate sizes based on a
    delimiter as well as the full parsing on complex sizes.
    """
    def test_split_commas(self):
        """
        Tests that the function used to seperate sizes with commas as the delimiter.
        """
        self.assertEqual(['L','M','S'], _comma_seperate_sizes('L,M,S'))
        self.assertEqual(['X-LARGE', 'LARGE', 'MEDIUM', 'SMALL'], _comma_seperate_sizes('X-LARGE,,LARGE,MEDIUM,SMALL'))
        self.assertEqual(['13', '12', '15', '18'], _comma_seperate_sizes('  13,  12,   15,,,18'))
        self.assertEqual(['12', '24'], _comma_seperate_sizes('12, 24'))
        self.assertEqual(['12', '24'], _comma_seperate_sizes('12,24'))
        self.assertEqual(['12', '24'], _comma_seperate_sizes('12 , 24'))
        self.assertEqual(['32'], _comma_seperate_sizes('32,'))
        self.assertEqual(['32'], _comma_seperate_sizes('32,   '))

    def test_split_hyphens(self):
        """
        Tests the function used to seperate sizes with hyphens as the delimiter.
        """
        # tests against reasonable inputs directly or derived from data
        self.assertEqual(['32', '32', '34', '25'], _hyphen_seperate_sizes('32 - 32 - 34 - 25'))
        self.assertEqual(['32 32 32'], _hyphen_seperate_sizes('32 32 32')) # for now
        self.assertEqual(['32', '32', '32'], _hyphen_seperate_sizes('32    - 32     - 32')) # double check if desired behavior against data
        self.assertEqual(['32', '32'], _hyphen_seperate_sizes('32 --------- -- - - -32')) # double check if desired behavior against data also
        self.assertEqual(['L', 'M', 'S'], _hyphen_seperate_sizes('L - M - S'))
        self.assertEqual(['L', 'M', 'S'], _hyphen_seperate_sizes('L -- M -- S'))
        self.assertEqual(['X-SMALL'], _hyphen_seperate_sizes('X-SMALL'))
        self.assertEqual(['M(6-8)'], _hyphen_seperate_sizes('M(6-8)'))
        self.assertEqual(['S-30IN-75CM'], _hyphen_seperate_sizes('S-30IN-75CM'))
        self.assertEqual(['SMALL (32 - 34)', 'MEDIUM (34 - 36)'], _hyphen_seperate_sizes('SMALL (32 - 34) - MEDIUM (34 - 36)'))
        self.assertEqual(['XS B-C CUP', 'XS D CUP', 'SM B-C CUP', 'SM D CUP', 'LXL B-C', 'LXL D CUP'], _hyphen_seperate_sizes('XS B-C CUP - XS D CUP - SM B-C CUP - SM D CUP - LXL B-C - LXL D CUP'))

        # testing against malformed input
        self.assertEqual(['SMALL - '], _hyphen_seperate_sizes('SMALL - '))
        self.assertEqual(['MEDIUM (32 - 35) - SMALL (34'], _hyphen_seperate_sizes('MEDIUM (32 - 35) - SMALL (34'))

        # no hard and fast interpretation for correctness
        self.assertEqual(['MEDIUM', 'SMALL'], _hyphen_seperate_sizes('MEDIUM -SMALL'))
        self.assertEqual(['MEDIUM- SMALL'], _hyphen_seperate_sizes('MEDIUM- SMALL'))
        self.assertEqual(['MEDIUM-SMALL'], _hyphen_seperate_sizes('MEDIUM-SMALL'))

    def test_size_parsing(self):
        """
        Tests the full ability to seperate sizes for use in the product processing data feeds.
        Tests the basic cases and mixes the delimiter to ensure proper hierachy among delimiters
        is enforced.
        """
        self.assertEqual(['L','M','S'], seperate_sizes('L,M,S'))
        self.assertEqual(['32', '32', '34', '25'], seperate_sizes('32 - 32 - 34 - 25'))
        self.assertEqual(['SMALL (32 - 34)', 'MEDIUM (36 - 38)'], seperate_sizes('SMALL (32 - 34), MEDIUM (36 - 38)'))
        self.assertEqual(['SMALL (32-34)', 'MEDIUM (36-38)'], seperate_sizes('SMALL (32-34), MEDIUM (36-38)'))
        self.assertEqual(['X-LARGE', 'LARGE', 'MEDIUM'], seperate_sizes('X-LARGE, LARGE, MEDIUM'))
        self.assertEqual(['EU 37 / US 7 - 7.5'], seperate_sizes('EU 37 / US 7 - 7.5'))
        self.assertEqual(['X-SMALL'], seperate_sizes('X-SMALL'))
        self.assertEqual(['28 (2-4)'], seperate_sizes('28 (2-4)'))
        self.assertEqual(['20-22/L'], seperate_sizes('20-22/L'))
        self.assertEqual(['LARGE/X-LARGE'], seperate_sizes('LARGE/X-LARGE'))
        # self.assertEqual(['11 - 12 YEARS (US)'], seperate_sizes('11 - 12 YEARS (US)')) # hopefully will be removed when products correctly filtered by age
        self.assertEqual(['LARGE/X-LARGE','MEDIUM','X-SMALL/SMALL'], seperate_sizes('LARGE/X-LARGE,MEDIUM,X-SMALL/SMALL'))
        self.assertEqual(['LARGE (10)','SMALL(2-4)','XSMALL(12-18 MONTHS)','XXSMALL(6-9 MONTHS)'], seperate_sizes('LARGE (10),SMALL(2-4),XSMALL(12-18 MONTHS),XXSMALL(6-9 MONTHS),'))



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
