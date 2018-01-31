# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from product_feed_py.pepperjam import generate_product_id

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
