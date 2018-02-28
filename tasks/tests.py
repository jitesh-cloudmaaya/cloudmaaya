# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from product_feed_py.pepperjam import generate_product_id
from product_feed_py.mappings import *
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

class SizeTestCase(TestCase):
    """
    Tests the allume size parsing behavior. The mappings might be a bit amorphous so the test constraints
    are not hard and fast, but should be a good guide to enforce correct behavior of determining an allume
    size, given the current restraints, such as the lack of support for parsing sizes containing slashes.
    """
    fixtures = ['SizeMap', 'ShoeSizeMap', 'SizeTermMap']

    def test_determine_allume_size_shoe(self):
        # setup
        # categories of interest / with special rules
        allume_category = 'Shoes'
        # initialize mappings
        size_mapping = create_size_mapping()
        shoe_size_mapping = create_shoe_size_mapping()
        size_term_mapping = create_size_term_mapping()

        # current rules happy path logic testing
        self.assertEqual('8', determine_allume_size(allume_category, '8', size_mapping, shoe_size_mapping, size_term_mapping))
        self.assertEqual('7 Medium', determine_allume_size(allume_category, '7M', size_mapping, shoe_size_mapping, size_term_mapping))
        self.assertEqual('6 & 6.5', determine_allume_size(allume_category, '39', size_mapping, shoe_size_mapping, size_term_mapping))
        self.assertEqual('7 & 7.5', determine_allume_size(allume_category, '40', size_mapping, shoe_size_mapping, size_term_mapping))
        self.assertEqual('37', determine_allume_size(allume_category, '37 (7)', size_mapping, shoe_size_mapping, size_term_mapping))
        self.assertEqual('8.5 & 9', determine_allume_size(allume_category, '42 (9)', size_mapping, shoe_size_mapping, size_term_mapping))
        self.assertEqual('8.5 Wide', determine_allume_size(allume_category, '8.5W', size_mapping, shoe_size_mapping, size_term_mapping))
        self.assertEqual('10 Narrow', determine_allume_size(allume_category, '10N', size_mapping, shoe_size_mapping, size_term_mapping))
        self.assertEqual('8 Wide', determine_allume_size(allume_category, '8WW', size_mapping, shoe_size_mapping, size_term_mapping))
        self.assertEqual('8 Medium', determine_allume_size(allume_category, '8 M', size_mapping, shoe_size_mapping, size_term_mapping))
        self.assertEqual('6 & 6.5 Medium', determine_allume_size(allume_category, '39 M (6 US)', size_mapping, shoe_size_mapping, size_term_mapping))

        # unsupported terms ?
        self.assertEqual('6B', determine_allume_size(allume_category, '6B', size_mapping, shoe_size_mapping, size_term_mapping))
        self.assertEqual('7.5B / 37.5EU', determine_allume_size(allume_category, '7.5B / 37.5EU', size_mapping, shoe_size_mapping, size_term_mapping))
        self.assertEqual('EURO35/US4/UK2', determine_allume_size(allume_category, 'EURO35/US4/UK2', size_mapping, shoe_size_mapping, size_term_mapping))
        
        # unexpected / malformed 
        self.assertEqual('5,6,7,8', determine_allume_size(allume_category, '5,6,7,8', size_mapping, shoe_size_mapping, size_term_mapping))
        self.assertEqual('REGULAR', determine_allume_size(allume_category, 'REGULAR', size_mapping, shoe_size_mapping, size_term_mapping))

        # not sure if desired behavior (see also below)
        self.assertEqual('22EU', determine_allume_size(allume_category, '22 EU (6 US)', size_mapping, shoe_size_mapping, size_term_mapping))

        return
        # additional problem cases, refine?
        self.assertEqual('35 (5),35.5 (5.5),36 (6),36.5 (6.5),37 (7),37.5 (7.5),38 (8),38.5 (8.5),39 (9),39.5 (9.5),40 (10),40.5 (10.5),41 (11)', determine_allume_size(allume_category, '35 (5),35.5 (5.5),36 (6),36.5 (6.5),37 (7),37.5 (7.5),38 (8),38.5 (8.5),39 (9),39.5 (9.5),40 (10),40.5 (10.5),41 (11)', size_mapping, shoe_size_mapping, size_term_mapping))

    def test_determine_allume_size(self):
        # setup
        # categories of interest/ with special rules
        allume_category = 'Other'
        # initialize mappings
        size_mapping = create_size_mapping()
        shoe_size_mapping = create_shoe_size_mapping()
        size_term_mapping = create_size_term_mapping()

        self.assertEqual('L', determine_allume_size(allume_category, 'LARGE', size_mapping, shoe_size_mapping, size_term_mapping))
        self.assertEqual('14 & 16', determine_allume_size(allume_category, '1X', size_mapping, shoe_size_mapping, size_term_mapping))
        self.assertEqual('4 & 27 & S', determine_allume_size(allume_category, '27', size_mapping, shoe_size_mapping, size_term_mapping))
        self.assertEqual('4', determine_allume_size(allume_category, '4 (XL)', size_mapping, shoe_size_mapping, size_term_mapping))
        self.assertEqual('4 Petite', determine_allume_size(allume_category, '4P', size_mapping, shoe_size_mapping, size_term_mapping))
        self.assertEqual('5 Medium', determine_allume_size(allume_category, '5M', size_mapping, shoe_size_mapping, size_term_mapping))
        self.assertEqual('18 Wide', determine_allume_size(allume_category, '18W', size_mapping, shoe_size_mapping, size_term_mapping))


        # self.assertEqual('', determine_allume_size(allume_category, '23INCH', size_mapping, shoe_size_mapping, size_term_mapping))
        # 00 & 23 & XXSINCH

        # unexpected / malformed
        self.assertEqual('52X84', determine_allume_size(allume_category, '52X84', size_mapping, shoe_size_mapping, size_term_mapping))
        self.assertEqual('9-11', determine_allume_size(allume_category, '9-11', size_mapping, shoe_size_mapping, size_term_mapping))

        # not sure if desired behavior (see above)
        self.assertEqual('3.3OZ.', determine_allume_size(allume_category, '3.3 OZ.', size_mapping, shoe_size_mapping, size_term_mapping))
        self.assertEqual('44IT', determine_allume_size(allume_category, '44 IT (10 US)', size_mapping, shoe_size_mapping, size_term_mapping))

        return # problem cases occuring with lingerie?
        self.assertEqual('32DDD', determine_allume_size(allume_category, '32DDD', size_mapping, shoe_size_mapping, size_term_mapping))
        return
        # future support?
        self.assertEqual('M Petite', determine_allume_size(allume_category, 'P/M', size_mapping, shoe_size_mapping, size_term_mapping))



# "35 (5),35.5 (5.5),36 (6),36.5 (6.5),37 (7),37.5 (7.5),38 (8),38.5 (8.5),39 (9),39.5 (9.5),40 (10),40.5 (10.5),41 (11)","35","Shoes","233"

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
