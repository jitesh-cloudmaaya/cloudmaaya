# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from .product_feed_py.mappings import *

# Create your tests here.

class MappingsTestCase(TestCase):
    """
    Some simple tests to confirm that mappings return a structure like we expect.
    Changes like changes to the database table names should not break the mappings helpers,
    these tests should quickly confirm basic sanity.
    """

    fixtures = ['MappingsTestCase']

    def test_merchant_mapping(self):
        """
        Tests that a call to create_merchant_mapping creates a dictionary with the
        expected structure: {long merchant_id: int active}
        """
        merchant_mapping = create_merchant_mapping()
        self.assertIsNotNone(merchant_mapping)
        # print merchant_mapping

        # general structure
        self.assertTrue(isinstance(merchant_mapping.keys()[0], long))
        self.assertTrue(isinstance(merchant_mapping.values()[0], int))

        # fixture specific
        # self.assertEqual(1, merchant_mapping.keys()[0])

    def test_color_mapping(self):
        """
        Tests that a call to create_color_mapping creates a dictionary with the
        expected structure: {str external_color: str allume_color}
        """
        color_mapping = create_color_mapping()
        self.assertIsNotNone(color_mapping)

        # general structure
        self.assertTrue(isinstance(color_mapping.keys()[0], unicode))
        self.assertTrue(isinstance(color_mapping.values()[0], unicode))

        # fixture specific
        self.assertEqual(u'brown', color_mapping[color_mapping.keys()[0]])

    def test_category_mapping(self):
        """
        Tests that a call to create_category_mapping create a dictionary with the
        expected structure: {(str primary_category, str secondary_category):
        (int allume_category_id, int active)}
        """
        category_mapping = create_category_mapping()
        self.assertIsNotNone(category_mapping)

        # general structure
        k = category_mapping.keys()[0]
        v = category_mapping.values()[0]
        self.assertTrue(isinstance(k, tuple))
        self.assertTrue(isinstance(k[0], unicode))
        self.assertTrue(isinstance(k[1], unicode))
        self.assertTrue(isinstance(v, tuple))
        self.assertTrue(isinstance(v[0], long))
        self.assertTrue(isinstance(v[1], int))

        # fixture specific
        info = category_mapping[k]
        self.assertEqual(1, info[0])
        self.assertEqual(1, info[1])

    def test_allume_category_mapping(self):
        """
        Tests that a call to create_category_mapping creates a dictionary with the
        expected structure: {long id: (unicode name, int active)}
        """
        allume_category_mapping = create_allume_category_mapping()
        self.assertIsNotNone(allume_category_mapping)

        # general structure
        self.assertTrue(isinstance(allume_category_mapping.keys()[0], long))
        v = allume_category_mapping.values()[0]
        self.assertTrue(isinstance(v, tuple))
        self.assertTrue(isinstance(v[0], unicode))
        self.assertTrue(isinstance(v[1], int))

        # fixture specific
        info = allume_category_mapping[allume_category_mapping.keys()[0]]
        self.assertEqual(u'Test Allume Category', info[0])
        self.assertEqual(1, info[1])
 