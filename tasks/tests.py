# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from product_feed_py.pepperjam import generate_product_id_pepperjam
from product_feed_py.mappings import *
from product_feed_py.mappings import _check_exclusion_terms, _check_other_term_maps
from product_feed_py.product_feed_helpers import *
from product_feed_py.product_feed_helpers import _hyphen_seperate_sizes, _comma_seperate_sizes

# Create your tests here.
class GenerateProductIdTestCase(TestCase):
    """
    Simple tests to make sure attributes of the generated product id are within expectations.
    That is, ensure that the generated product_ids only consist of numeric characters, have a
    length no greater than 19, etc.
    """

    def test_generate_product_id_pepperjam(self):
        # both sku and merchant id are numeric
        self.assertEqual(u'82197041558', generate_product_id_pepperjam(u'821970', u'41558'))
        # sku contains alphabetic characters
        self.assertEqual(u'15164794137793', generate_product_id_pepperjam(u'OP47941', u'37793'))
        self.assertEqual(u'1911211696348333530', generate_product_id_pepperjam(u'sku169634833', u'35300'))
        # sku contains non alphanumeric characters
        self.assertEqual(u'2621268302324973024', generate_product_id_pepperjam(u'ZUZH-WX97-XS', u'41846'))
        # sku + merchant id is very long
        self.assertEqual(u'6592220150063020212', generate_product_id_pepperjam(u'65IVTO006-TUVMQU5HRSBHUkVZ0', u'38014'))


class ProductFeedHelpersTestCase(TestCase):
    """
    Tests the behavior of the methods used in product_feed_helpers.py. Useful for determining the behavior
    of the methods across network data feeds to ascertain whether the error is in the helper or the method
    of application. Furthermore, has uses in maintaining appropriate behavior of the functions even as 
    more requirements are illuminated.
    """

    fixtures = ['SynonymCategoryMap', 'ExclusionTerm', 'AllumeCategory']

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

    def test_parse_category_from_product_name(self):
        # now need to initialize the synonym category mapping
        synonym_category_mapping = create_synonym_category_mapping()
        exclusion_terms = create_exclusion_term_mapping()

        # working for take 1
        self.assertEqual('', parse_category_from_product_name('', synonym_category_mapping, exclusion_terms))
        self.assertEqual('', parse_category_from_product_name('Hopefully Some terms that stay not synonyms', synonym_category_mapping, exclusion_terms))
        self.assertEqual('Shoes', parse_category_from_product_name('Zerogrand Slip-On  Flat', synonym_category_mapping, exclusion_terms))
        self.assertEqual('Bottoms', parse_category_from_product_name('Under Armour Fly Fast HeatGear Capri Leggings', synonym_category_mapping, exclusion_terms))
        self.assertEqual('', parse_category_from_product_name('Polosko Lace-Up Platform', synonym_category_mapping, exclusion_terms))
        self.assertEqual('Tops', parse_category_from_product_name('Pratt Denim Button Up', synonym_category_mapping, exclusion_terms))
        self.assertEqual('Other', parse_category_from_product_name('Loungewear Lingerie', synonym_category_mapping, exclusion_terms))
        self.assertEqual('Accessories', parse_category_from_product_name('Winter Hat', synonym_category_mapping, exclusion_terms))
        self.assertEqual('Tops', parse_category_from_product_name('Low-Top', synonym_category_mapping, exclusion_terms))

        # assertions for take 2
        self.assertEqual('Shoes',  parse_category_from_product_name('Dress Shoes', synonym_category_mapping, exclusion_terms))
        self.assertEqual('Shoes',  parse_category_from_product_name('Low Top Shoes', synonym_category_mapping, exclusion_terms))
        self.assertEqual('Dresses',  parse_category_from_product_name('Knit Dress', synonym_category_mapping, exclusion_terms))
        self.assertEqual('Jackets',  parse_category_from_product_name('Shorts Collared Jackets', synonym_category_mapping, exclusion_terms))
        self.assertEqual('Shoes',  parse_category_from_product_name('Top Bottom Heels Nothing', synonym_category_mapping, exclusion_terms))
        self.assertEqual('Bottoms',  parse_category_from_product_name('Button Up Britches', synonym_category_mapping, exclusion_terms))
        self.assertEqual('Jackets',  parse_category_from_product_name('Flat Facing Jacket', synonym_category_mapping, exclusion_terms))
        self.assertEqual('Jackets',  parse_category_from_product_name('Gown Down Overcoat Moat', synonym_category_mapping, exclusion_terms))
        self.assertEqual('Tops',  parse_category_from_product_name('Button Up Mock Neck Empty', synonym_category_mapping, exclusion_terms))
        self.assertEqual('Bottoms', parse_category_from_product_name('Dyed Boot Cut Jeans by Everlane', synonym_category_mapping, exclusion_terms))

        # assertions for take 3
        # 1) exclude overrides all
        self.assertEqual('Exclude', parse_category_from_product_name("Kid's Shoes", synonym_category_mapping, exclusion_terms)) # would formerly map to shoes, should now map to exclude
        self.assertEqual('Exclude', parse_category_from_product_name("trimmed jeans beverages tunic slippers purse bracelet cap", synonym_category_mapping, exclusion_terms))
        self.assertEqual('Exclude', parse_category_from_product_name("fragrance boys", synonym_category_mapping, exclusion_terms))
        # other should lose to exclude
        self.assertEqual('Exclude', parse_category_from_product_name('Beverages maternity watch', synonym_category_mapping, exclusion_terms))# should map to exclude instaad of other

        # 2) if an other term is in the product name, it will overrule alternative synonym categories that are also present
        self.assertEqual('Other', parse_category_from_product_name('Purse bra hoodie', synonym_category_mapping, exclusion_terms)) # since contains hte exclusion term, bra, should map to Other instead of Tops from 'hoodie'
        self.assertEqual('Other', parse_category_from_product_name('phone tunic slippers purse backpack', synonym_category_mapping, exclusion_terms))
        self.assertEqual('Other', parse_category_from_product_name('ankle jeans slippers choker swimsuit', synonym_category_mapping, exclusion_terms))

    def test_tiered_assignment(self):
        """
        Tests the product_field_tiered_assignment function helper used in the RAN clean data method.
        """
        # datum is a dictionary of field type names to field values
        # tiered assignments is a dictionary of fields with multiple assignment possibilities and a list of field type assignment possibilities
        # fieldname is the initial fieldname
        # 4th arg is a default string value to use in the event that there is no tiered assignment defined for that product fieldname

        # typical case
        tiered_assignments = {'primary_category': ["datum['primary_category']", "datum['attribute_2_product_type']"]}
        fieldname = 'primary_category'
        datum = {'primary_category': 'groomingfragrance', 'attribute_2_product_type': 'Beauty & Fragrance'}
        self.assertEqual('groomingfragrance', product_field_tiered_assignment(tiered_assignments, fieldname, datum, datum['primary_category']))

        tiered_assignments = {'primary_category': ["datum['attribute_2_product_type']", "datum['primary_category']"]}
        fieldname = 'primary_category'
        datum = {'primary_category': 'groomingfragrance', 'attribute_2_product_type': 'Beauty & Fragrance'}
        self.assertEqual('Beauty & Fragrance', product_field_tiered_assignment(tiered_assignments, fieldname, datum, datum['primary_category']))

        # no tiered assignments case
        tiered_assignments = {}
        fieldname = 'primary_category'
        datum = {'primary_category': 'groomingfragrance', 'attribute_2_product_type': 'Beauty & Fragrance'}
        self.assertEqual('groomingfragrance', product_field_tiered_assignment(tiered_assignments, fieldname, datum, datum['primary_category']))

        # use one of the alternatives case
        tiered_assignments = {'primary_category': ["datum['primary_category']", "datum['attribute_2_product_type']"]}
        fieldname = 'primary_category'
        datum = {'primary_category': '', 'attribute_2_product_type': 'Beauty & Fragrance'}
        self.assertEqual('Beauty & Fragrance', product_field_tiered_assignment(tiered_assignments, fieldname, datum, datum['primary_category']))

        # exhaust the alternatives case
        tiered_assignments = {'primary_category': ["datum['primary_category']", "datum['attribute_2_product_type']"]}
        fieldname = 'primary_category'
        datum = {'primary_category': '', 'attribute_2_product_type': ''}
        self.assertEqual('', product_field_tiered_assignment(tiered_assignments, fieldname, datum, datum['primary_category']))

        # test the method case
        synonym_category_mapping = create_synonym_category_mapping()
        exclusion_terms = create_exclusion_term_mapping()

        tiered_assignments = {'secondary_category': ["datum['secondary_category']", "parse_category_from_product_name(datum['product_name'], kwargs['synonym_category_mapping'], kwargs['exclusion_terms'])"]}
        fieldname = 'secondary_category'
        datum = {'product_name': 'Lacoste Holiday Pique Polo', 'secondary_category': ''}
        self.assertEqual('Tops', product_field_tiered_assignment(tiered_assignments, fieldname, datum, datum['secondary_category'], synonym_category_mapping = synonym_category_mapping, exclusion_terms = exclusion_terms))

        tiered_assignments = {'secondary_category': ["datum['secondary_category']", "parse_category_from_product_name(datum['product_name'], kwargs['synonym_category_mapping'], kwargs['exclusion_terms'])"]}
        fieldname = 'secondary_category'
        datum = {'product_name': 'Lacoste Holiday Pique Polo', 'secondary_category': 'groomingfragrance'}
        self.assertEqual('groomingfragrance', product_field_tiered_assignment(tiered_assignments, fieldname, datum, datum['secondary_category'], synonym_category_mapping = synonym_category_mapping, exclusion_terms = exclusion_terms))

        # test the new default behavior
        tiered_assignments = {}
        fieldname = 'product_name'
        datum = {'product_name': 'Lacoste Holiday Pique Polo'}
        self.assertEqual('Lacoste Holiday Pique Polo', product_field_tiered_assignment(tiered_assignments, fieldname, datum, datum['product_name']))

    def test__check_exclusion_terms(self):
        """
        The list of ExclusionTerms is found in ExclusionTerm.yaml.
        """
        exclusion_terms = ExclusionTerm.objects.values_list('term', flat = True)

        self.assertEqual(False, _check_exclusion_terms("", "", exclusion_terms))
        self.assertEqual(False, _check_exclusion_terms("neither", "", exclusion_terms))
        self.assertEqual(False, _check_exclusion_terms("", "either", exclusion_terms))
        self.assertEqual(False, _check_exclusion_terms("both", "some", exclusion_terms))
        self.assertEqual(True, _check_exclusion_terms("kid's", "", exclusion_terms))
        self.assertEqual(True, _check_exclusion_terms("", "kid's", exclusion_terms))
        self.assertEqual(True, _check_exclusion_terms("good", "food", exclusion_terms))
        self.assertEqual(True, _check_exclusion_terms("not an exclusion", "barbies", exclusion_terms))
        self.assertEqual(True, _check_exclusion_terms("home", "test", exclusion_terms))
        self.assertEqual(False, _check_exclusion_terms("toddlerstodo", "", exclusion_terms))
        self.assertEqual(True, _check_exclusion_terms("entertainment-now", "", exclusion_terms))

    def test_add_category_map(self):
        exclusion_terms = ExclusionTerm.objects.values_list('term', flat = True)
        synonym_other_terms = SynonymCategoryMap.objects.filter(category = 'Other').values_list('synonym', flat=True)
        synonym_terms = SynonymCategoryMap.objects.values_list('category', flat=True)

        ac_JACKETS = AllumeCategory.objects.get(name__iexact='Jackets')
        ac_TOPS = AllumeCategory.objects.get(name__iexact='Tops')
        ac_DRESSES = AllumeCategory.objects.get(name__iexact='Dresses')

        add_category_map('Tops > Shirts-Blouses,Clearance > Redlines-Clearance,Apparel > Tops > All-Tops,Clearance > Redlines-Tops', 'Jackets', 'test merchant', exclusion_terms, synonym_other_terms, synonym_terms)
        cm = CategoryMap.objects.last()
        self.assertEqual(ac_JACKETS, cm.allume_category)
        self.assertEqual(True, cm.turned_on)
        self.assertEqual(False, cm.pending_review)

        add_category_map('Apparel > Jackets > All-Jackets,Clearance > Redlines-Tops,Accessories > Wraps-Cover-Ups-Ponchos', 'Tops', 'test merchant', exclusion_terms, synonym_other_terms, synonym_terms)
        cm = CategoryMap.objects.last()
        self.assertEqual(ac_TOPS, cm.allume_category)
        self.assertEqual(True, cm.turned_on)
        self.assertEqual(False, cm.pending_review)

        add_category_map('Clearance > Redlines-Accessories,Apparel > Sweaters > All-Sweaters,Clearance > Redlines-Sweaters,Accessories > Wraps-Cover-Ups-Ponchos', 'Tops', 'test merchant', exclusion_terms, synonym_other_terms, synonym_terms)
        cm = CategoryMap.objects.last()
        self.assertEqual(ac_TOPS, cm.allume_category)
        self.assertEqual(True, cm.turned_on)
        self.assertEqual(False, cm.pending_review)

        add_category_map('New-Arrivals > Online-Exclusives,Petite-Tall-Plus > Petites > Tops-Sweaters,Petite-Tall-Plus > Petites > All-Petites,Apparel > Online-Exclusives > Petite,Clearance > Redlines-Online-Exclusives,Apparel > Online-Exclusives > All-Exclusives,Clearance > Redlines-Sweaters,Clearance > Redlines-Tops,Appare', 'Tops', 'test merchant', exclusion_terms, synonym_other_terms, synonym_terms)
        cm = CategoryMap.objects.last()
        self.assertEqual(ac_TOPS, cm.allume_category)
        self.assertEqual(True, cm.turned_on)
        self.assertEqual(False, cm.pending_review)

        add_category_map('Clearance > Redlines-Dresses,Apparel > Dresses > All-Dresses,Clearance > Redlines-Online-Exclusives,Apparel > Online-Exclusives > All-Exclusives,Apparel > Online-Exclusives > Dresses-Skirts,Apparel > Dresses > Sweater,Apparel > Dresses > Midi-Sheaths', 'Dresses', 'test merchant', exclusion_terms, synonym_other_terms, synonym_terms)
        cm = CategoryMap.objects.last()
        self.assertEqual(ac_DRESSES, cm.allume_category)
        self.assertEqual(True, cm.turned_on)
        self.assertEqual(False, cm.pending_review)

    def test__check_other_term_maps(self):
        """
        The list of terms is found in OtherTermMap.yaml.
        """
        synonym_other_terms = SynonymCategoryMap.objects.filter(category = 'Other').values_list('synonym', flat=True)

        self.assertEqual(True, _check_other_term_maps('swimsuits2018', '', synonym_other_terms))
        self.assertEqual(True, _check_other_term_maps('', 'swimsuits2018', synonym_other_terms))
        self.assertEqual(True, _check_other_term_maps('maternity', '', synonym_other_terms))
        self.assertEqual(True, _check_other_term_maps('lingerie-match', '', synonym_other_terms))
        self.assertEqual(True, _check_other_term_maps('swimsuits', 'nothing', synonym_other_terms))
        self.assertEqual(True, _check_other_term_maps('hmmm', 'swimsuits', synonym_other_terms))
        self.assertEqual(True, _check_other_term_maps('maternityleave', 'swimsuits2018', synonym_other_terms))
        self.assertEqual(False, _check_other_term_maps('', '', synonym_other_terms))
        self.assertEqual(False, _check_other_term_maps('Apparel', '', synonym_other_terms))
        self.assertEqual(False, _check_other_term_maps('Apparel', 'Accessories', synonym_other_terms))
        self.assertEqual(False, _check_other_term_maps('', 'Accessories', synonym_other_terms))

    def test_add_category_map_w_exclusion_term(self):
        exclusion_terms = ExclusionTerm.objects.values_list('term', flat = True)
        synonym_other_terms = SynonymCategoryMap.objects.filter(category = 'Other').values_list('synonym', flat=True)
        synonym_terms = SynonymCategoryMap.objects.values_list('category', flat=True)
        ac = AllumeCategory.objects.first()
        add_category_map('Clothing', 'Food', 'Raybeam', exclusion_terms, synonym_other_terms, synonym_terms, allume_category = ac)
        cm = CategoryMap.objects.get(external_cat1 = 'clothing', external_cat2 = 'food', merchant_name = 'Raybeam')
        exclude = AllumeCategory.objects.get(name__iexact='exclude')

        self.assertEqual(exclude, cm.allume_category)
        self.assertEqual(False, cm.turned_on)
        self.assertEqual(False, cm.pending_review)


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

    def test_determine_allume_size(self):
        # setup
        # categories of interest/ with special rules
        allume_category = 'Other'
        # initialize mappings
        size_mapping = create_size_mapping()
        shoe_size_mapping = create_shoe_size_mapping()
        size_term_mapping = create_size_term_mapping()

        self.assertEqual('L', determine_allume_size(allume_category, 'LARGE', size_mapping, shoe_size_mapping, size_term_mapping))
        self.assertEqual('14 & 16 Plus', determine_allume_size(allume_category, '1X', size_mapping, shoe_size_mapping, size_term_mapping))
        self.assertEqual('4 & 27 & S', determine_allume_size(allume_category, '27', size_mapping, shoe_size_mapping, size_term_mapping))
        self.assertEqual('4 & S', determine_allume_size(allume_category, '4 (XL)', size_mapping, shoe_size_mapping, size_term_mapping))
        self.assertEqual('4 & S Petite', determine_allume_size(allume_category, '4P', size_mapping, shoe_size_mapping, size_term_mapping))
        self.assertEqual('5 Medium', determine_allume_size(allume_category, '5M', size_mapping, shoe_size_mapping, size_term_mapping))
        self.assertEqual('18 & XXL Wide Plus', determine_allume_size(allume_category, '18W', size_mapping, shoe_size_mapping, size_term_mapping))

        # unexpected / malformed
        self.assertEqual('52X84', determine_allume_size(allume_category, '52X84', size_mapping, shoe_size_mapping, size_term_mapping))
        self.assertEqual('9-11', determine_allume_size(allume_category, '9-11', size_mapping, shoe_size_mapping, size_term_mapping))

        # not sure if desired behavior (see above)
        self.assertEqual('3.3OZ.', determine_allume_size(allume_category, '3.3 OZ.', size_mapping, shoe_size_mapping, size_term_mapping))
        self.assertEqual('44IT', determine_allume_size(allume_category, '44 IT (10 US)', size_mapping, shoe_size_mapping, size_term_mapping))

        # return # problem cases occuring with lingerie?
        self.assertEqual('32DDD', determine_allume_size(allume_category, '32DDD', size_mapping, shoe_size_mapping, size_term_mapping))
        # return
        # future support?
        # self.assertEqual('M Petite', determine_allume_size(allume_category, 'P/M', size_mapping, shoe_size_mapping, size_term_mapping))


class SizeTestCase(TestCase):
    """
    Tests the allume size parsing behavior. The mappings might be a bit amorphous so the test constraints
    are not hard and fast, but should be a good guide to enforce correct behavior of determining an allume
    size, given the current restraints, such as the lack of support for parsing sizes containing slashes.
    """
    # fixtures = ['SizeMap', 'ShoeSizeMap', 'SizeTermMap']

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

    def test_determine_allume_size(self):
        # setup
        # categories of interest/ with special rules
        allume_category = 'Other'
        # initialize mappings
        size_mapping = create_size_mapping()
        shoe_size_mapping = create_shoe_size_mapping()
        size_term_mapping = create_size_term_mapping()

        self.assertEqual('L', determine_allume_size(allume_category, 'LARGE', size_mapping, shoe_size_mapping, size_term_mapping))
        self.assertEqual('14 & 16 Plus', determine_allume_size(allume_category, '1X', size_mapping, shoe_size_mapping, size_term_mapping))
        self.assertEqual('4 & 27 & S', determine_allume_size(allume_category, '27', size_mapping, shoe_size_mapping, size_term_mapping))
        self.assertEqual('4 & S', determine_allume_size(allume_category, '4 (XL)', size_mapping, shoe_size_mapping, size_term_mapping))
        self.assertEqual('4 & S Petite', determine_allume_size(allume_category, '4P', size_mapping, shoe_size_mapping, size_term_mapping))
        self.assertEqual('5 Medium', determine_allume_size(allume_category, '5M', size_mapping, shoe_size_mapping, size_term_mapping))
        self.assertEqual('18 & XXL Wide Plus', determine_allume_size(allume_category, '18W', size_mapping, shoe_size_mapping, size_term_mapping))

        # unexpected / malformed
        self.assertEqual('52X84', determine_allume_size(allume_category, '52X84', size_mapping, shoe_size_mapping, size_term_mapping))
        self.assertEqual('9-11', determine_allume_size(allume_category, '9-11', size_mapping, shoe_size_mapping, size_term_mapping))

        # not sure if desired behavior (see above)
        self.assertEqual('3.3OZ.', determine_allume_size(allume_category, '3.3 OZ.', size_mapping, shoe_size_mapping, size_term_mapping))
        self.assertEqual('44IT', determine_allume_size(allume_category, '44 IT (10 US)', size_mapping, shoe_size_mapping, size_term_mapping))

        # return # problem cases occuring with lingerie?
        self.assertEqual('32DDD', determine_allume_size(allume_category, '32DDD', size_mapping, shoe_size_mapping, size_term_mapping))


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


class CategoryHandlingTestCase(TestCase):
    """
    Test that the hierarchy on products is what is expected for adding catmaps and setting things etc.
    """
    fixtures = ['SynonymCategoryMap', 'ExclusionTerm', 'AllumeCategory']

    def test_add_category_map_set_allume_category(self):
        merchant_name = "Test Merchant"
        other_synonym = SynonymCategoryMap.objects.filter(category__iexact = 'Other').first().synonym
        exclusion_term = ExclusionTerm.objects.first().term
        OTHER = AllumeCategory.objects.get(name__iexact = 'Other')
        EXCLUDE = AllumeCategory.objects.get(name__iexact = 'Exclude')
        exclusion_terms = ExclusionTerm.objects.values_list('term', flat = True)
        synonym_other_terms = SynonymCategoryMap.objects.filter(category = 'Other').values_list('synonym', flat=True)
        synonym_terms = SynonymCategoryMap.objects.values_list('category', flat=True)

        self.assertEqual(0, CategoryMap.objects.count())
        add_category_map(other_synonym, '', merchant_name, exclusion_terms, synonym_other_terms, synonym_terms)
        cm  = CategoryMap.objects.last()
        self.assertEqual(OTHER, cm.allume_category)
        add_category_map('', exclusion_term, merchant_name, exclusion_terms, synonym_other_terms, synonym_terms)
        cm2  = CategoryMap.objects.last()
        self.assertEqual(EXCLUDE, cm2.allume_category)
        add_category_map(other_synonym, exclusion_term, merchant_name, exclusion_terms, synonym_other_terms, synonym_terms)
        cm3  = CategoryMap.objects.last()
        self.assertEqual(EXCLUDE, cm3.allume_category)

    def test_other_parsing(self):
        merchant_name = "Test Merchant"
        other_synonym = SynonymCategoryMap.objects.filter(category__iexact = 'Other').first().synonym
        synonym_other_category_mapping = create_synonym_other_category_mapping()
        tiered_assignments = {'secondary_category': ["parse_other_terms(datum['product_name'], kwargs['synonym_other_category_mapping'])", "datum['secondary_category']", "parse_category_from_product_name(datum['product_name'], kwargs['synonym_category_mapping'])"]}
        fieldname = 'secondary_category'
        datum = {'product_name': 'Product ' + other_synonym, 'primary_category': 'Apparel & Accessories', 'secondary_category': 'Should change?'}
        OTHER = AllumeCategory.objects.get(name__iexact = 'Other')
        exclusion_terms = ExclusionTerm.objects.values_list('term', flat = True)
        synonym_other_terms = SynonymCategoryMap.objects.filter(category = 'Other').values_list('synonym', flat=True)
        synonym_terms = SynonymCategoryMap.objects.values_list('category', flat=True)

        secondary_category = product_field_tiered_assignment(tiered_assignments, fieldname, datum, datum['secondary_category'], synonym_other_category_mapping = synonym_other_category_mapping)
        self.assertEqual('Other', secondary_category)
        self.assertEqual(0, CategoryMap.objects.count())
        add_category_map('', secondary_category, merchant_name, exclusion_terms, synonym_other_terms, synonym_terms)
        cm  = CategoryMap.objects.first()
        self.assertEqual(OTHER, cm.allume_category)
