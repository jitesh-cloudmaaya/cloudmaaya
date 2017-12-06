from elasticsearch_dsl import DocType, Completion
from elasticsearch_dsl.field import (
    String, Date as ESDate, Float, Boolean
)
from elasticsearch_dsl import FacetedSearch
from elasticsearch_dsl import TermsFacet, DateHistogramFacet, HistogramFacet, RangeFacet
from elasticsearch_dsl.query import Q
from six import itervalues
import collections

import inspect

from catalogue_service.settings_local import PRODUCT_INDEX
from six import iteritems, itervalues, string_types
"""
#Commenting out for now I expect to delete soon unless we decide to not use logstash for indexing

class Logs(DocType):
    product_id = String(analyzer='snowball')
    merchant_id = String(analyzer='snowball')
    product_name = String(analyzer='snowball')
    long_product_description = String(analyzer='snowball')
    short_product_description = String(analyzer='snowball')
    product_url = String(index='not_analyzed')
    product_image_url = String(index='not_analyzed')
    buy_url = String(index='not_analyzed')
    manufacturer_name = String(analyzer='snowball')
    manufacturer_part_number = String(analyzer='snowball')
    sku = String(analyzer='snowball')
    product_type = String(analyzer='snowball')
    discount = String(analyzer='snowball')
    discount_type = String(analyzer='snowball')
    sale_price = String(analyzer='snowball')
    retail_price = String(analyzer='snowball')
    shipping_price = String(analyzer='snowball')
    color = String(analyzer='snowball')
    gender = String(analyzer='snowball')
    style = String(analyzer='snowball')
    size = String(analyzer='snowball')
    material = String(analyzer='snowball')
    age = String(analyzer='snowball')
    currency = String(analyzer='snowball')
    availability = String(analyzer='snowball')
    begin_date = ESDate()
    end_date = ESDate()
    merchant_name = String(analyzer='snowball')
    created_at = ESDate()
    updated_at = ESDate()

    class Meta:
        index = "logstash-*"

    def save(self, **kwargs):
        return super(Email, self).save(** kwargs)

    @classmethod
    def properties(cls):
        return [
            prop for prop in
            Email._doc_type.mapping.properties.to_dict(
            )['email']['properties'].keys()
            if not prop.startswith('x_')
        ]
"""


class EProductSearch(FacetedSearch):
    doc_types = ['product']
    # fields that should be searched
    index = PRODUCT_INDEX

    fields = ['product_name', 'long_product_description', 'short_product_description', 'keywords', 'primary_category']
    price_ranges=[("$0-$25", (None, 25)), ("$25-$50", (25, 50)), ("$50-$100", (50, 100)), ("$100-$250", (100, 250)), ("$250-$500", (250, 500)), ("$500 And Up", (500, None))]
    
    facets = collections.OrderedDict((
        # use bucket aggregations to define facets
        ('manufacturer_name', TermsFacet(field='manufacturer_name.keyword', size=100)),
        ('color', TermsFacet(field='color.keyword', size=100)),
        ('merchant_name', TermsFacet(field='merchant_name.keyword', size=100)),
        ('style', TermsFacet(field='style.keyword', size=100)),
        ('size', TermsFacet(field='size.keyword', size=100)),
        ('gender', TermsFacet(field='gender.keyword', size=100)),
        ('age', TermsFacet(field='age.keyword', size=100)),
        ('brand', TermsFacet(field='brand.keyword', size=100)),
        ('material', TermsFacet(field='material.keyword')),
        ('primary_category', TermsFacet(field='primary_category.keyword', size=100)),
        ('allume_score', TermsFacet(field='allume_score')), #HistogramFacet
        ('is_trending', TermsFacet(field='is_trending')),
        ('is_best_seller', TermsFacet(field='is_best_seller')),
        ('price_range', RangeFacet(field='sale_price', ranges=price_ranges)), #current_price
    )) 

    def __init__(self, query=None, filters={}, sort=(), favs=[]):
        """
        :arg query: the text to search for
        :arg filters: facet values to filter
        :arg sort: sort information to be passed to :class:`~elasticsearch_dsl.Search`
        """
        self._favs = favs
        self._query = query
        self._filters = {}
        # TODO: remove in 6.0
        if isinstance(sort, string_types):
            self._sort = (sort,)
        else:
            self._sort = sort
        self.filter_values = {}
        for name, value in iteritems(filters):
            self.add_filter(name, value)

        self._s = self.build_search()


    def filter(self, search):
        """
        Over-ride default behaviour (which uses post_filter)
        to use filter instead.
        """

        print self._filters
        filters = Q('match_all')
        for f in itervalues(self._filters):
            filters &= f

        return search.filter(filters)



    def query(self, search, query):
        """Overriden to use bool AND by default"""

        if query == "*":
            main_q = Q({"match_all" : {}})
        else:            
            main_q = Q('multi_match',
                    fields=self.fields,
                    query=query,
                    operator='and'
                )

        #Add in Filter for Fav Products
        if self._favs:
            q_faves = Q({"ids" : {"values" : self._favs}})
        else:
            q_faves = Q()


        return search.query(main_q).query(q_faves)#.sort('-p')

"""
  "collapse": {
    "field": "product_name.keyword",
    "inner_hits": {
      "name": "collapsed_by_size",
      "from": 1,
      "size": 2
    }
  }
"""
