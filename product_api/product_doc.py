from elasticsearch_dsl import DocType, Completion
from elasticsearch_dsl.field import (
    String, Date as ESDate, Float, Boolean
)
from elasticsearch_dsl import FacetedSearch
from elasticsearch_dsl import TermsFacet, DateHistogramFacet, HistogramFacet, RangeFacet
from elasticsearch_dsl.connections import connections
from elasticsearch.helpers import bulk
from elasticsearch_dsl.query import Q
from six import itervalues
import collections

import inspect

from catalogue_service.settings_local import PRODUCT_INDEX
from six import iteritems, itervalues, string_types
from datetime import datetime, timedelta

from product_api.models import Merchant

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

    fields = ['product_name', 'long_product_description', 'short_product_description', 'keywords', 'primary_category^2', 'secondary_category^2', 'color^2', 'allume_category^10', 'merchant_color']
    price_ranges=[("$0 - $50", (0, 50)), ("$50 - $100", (50, 100)), ("$100 - $150", (100, 150)), ("$150 - $250", (150, 250)), ("$250 - $400", (250, 400)),("$400+", (400, None))]
    
    facets = collections.OrderedDict((
        # use bucket aggregations to define facets
        ('manufacturer_name', TermsFacet(field='manufacturer_name.keyword', size=100)),
        ('color', TermsFacet(field='color.keyword', size=100)),
        ('merchant_name', TermsFacet(field='merchant_name.keyword', size=100)),
        ('style', TermsFacet(field='style.keyword', size=100)),
        ('size', TermsFacet(field='allume_size.keyword', size=100)),
        ('gender', TermsFacet(field='gender.keyword', size=100)),
        ('age', TermsFacet(field='age.keyword', size=100)),
        ('brand', TermsFacet(field='brand.keyword', size=100)),
        ('material', TermsFacet(field='material.keyword')),
        ('primary_category', TermsFacet(field='allume_category.keyword', size=100)),
        ('allume_score', TermsFacet(field='allume_score')), #HistogramFacet
        ('is_trending', TermsFacet(field='is_trending')),
        ('is_best_seller', TermsFacet(field='is_best_seller')),
        ('price_range', RangeFacet(field='current_price', ranges=price_ranges)), #current_price
    )) 

    def __init__(self, query=None, filters={}, sort="_score", favs=[], card_count = False):
        """
        :arg query: the text to search for
        :arg filters: facet values to filter
        :arg sort: sort information to be passed to :class:`~elasticsearch_dsl.Search`
        """
        self._favs = favs
        self._query = query
        self._filters = {}
        self._card_count = card_count
        # TODO: remove in 6.0
        #if isinstance(sort, string_types):
        #    self._sort = (sort,)
        #else:
        self._sort = sort
        self.filter_values = {}
        for name, value in iteritems(filters):
            self.add_filter(name, value)

        self._s = self.build_search()

    @classmethod
    def sort_options(cls):
        return ['current_price', 'size.keyword', 'brand.keyword', 'merchant_name.keyword', 'allume_score']

    def filter(self, search):
        """
        Over-ride default behaviour (which uses post_filter)
        to use filter instead.
        """

        #print self._filters
        filters = Q('match_all')
        for f in itervalues(self._filters):
            filters &= f

        return search.filter(filters)


    def aggregate(self, search):
        """
        Add aggregations representing the facets selected, including potential
        filters.
        """
        for f, facet in iteritems(self.facets):
            agg = facet.get_aggregation()
            agg_filter = Q('match_all')
            for field, filter in iteritems(self._filters):
                if f == field:
                    continue
                agg_filter &= filter
            search.aggs.bucket(
                '_filter_' + f,
                'filter',
                filter=agg_filter
            ).bucket(f, agg)

    def query(self, search, query):
        """Overriden to use bool AND by default"""
        print '==============================================================='
        print self._filters
        print '==============================================================='


        if query == "*":
            main_q = Q({"match_all" : {}})
        else:            
            main_q = Q('multi_match',
                    fields=self.fields,
                    query=query,
                    type='cross_fields',
                    #type='cross_fields',
                    operator='and',
                    #custom_score={"query" : {"match_all" : {}},"script" : "_score * (10 - doc.allume_score.doubleValue)"},
                   # fuzziness="Auto",
                   # prefix_length=2,
                    #analyzer="my_synonyms"
                   # auto_generate_synonyms_phrase_query="true"
                )

        #Add in Filter for Fav Products
        if self._favs:
            q_faves = Q({"ids" : {"values" : self._favs}})
        else:
            q_faves = Q()

        #filter for In-Stock & Deleted
        q_available = Q({"match": {"availability": {"query": "in-stock", "type": "phrase"}}})
        q_not_deleted = Q({"match": {"is_deleted": {"query": "false", "type": "phrase"}}})

        collapse_dict = {"field": "raw_product_url.keyword","inner_hits": {"name": "collapsed_by_product_name","from": 1}}
        cardinality_dict = {"unique_count" : {"cardinality" : {"field" : "raw_product_url.keyword"}}}

# example of OR query from kibana
# GET products/_search
# {
#   "query": {
#     "query_string": {
#       "default_field": "merchant_name",
#       "query": "(Madewell) OR (Sole Society) OR (Saks Fifth Avenue)"
#     }
#   }
# }
        # need to apply query clause in "filter context" to yes or no answer to merchant_name memberbship

        # if merchant filter is not used... include all products from 'sizeless' merchants
        # will need to build the actual query using a merchant filter
        sizeless_merchant_names = Merchant.objects.filter(has_size_data=False).values_list('name', flat=True)
        if sizeless_merchant_names.count():
            q_sizeless_merchants = Q({"match": {"merchant_name": {"query": sizeless_merchant_names.first(), "type": "phrase"}}})
            sizeless_merchant_names = sizeless_merchant_names[1:]
            for merchant_name in sizeless_merchant_names:
                q_sizeless_merchants |= Q({"match": {"merchant_name": {"query": merchant_name, "type": "phrase"}}})
        # add in like so: search.query('bool', filter=[q_sizeless_merchants])

        # construct the supplemental query to match main_q
        if query == "*":
            supplemental_q = Q({"match_all": {}})
        else:
            supplemental_q = Q('multi_match',
                    fields=self.fields,
                    query=query,
                    type='cross_fields',
                    #type='cross_fields',
                    operator='and',
                    #custom_score={"query" : {"match_all" : {}},"script" : "_score * (10 - doc.allume_score.doubleValue)"},
                   # fuzziness="Auto",
                   # prefix_length=2,
                    #analyzer="my_synonyms"
                   # auto_generate_synonyms_phrase_query="true"
                )

        supplemental_q = Q('bool',
            must=[q_sizeless_merchants],
            should=[Q('match', product_name=query)],
            minimum_should_match=1
        )

        # we've built the search for products with no size data merchants clause
        # we and this with the main query used, except we should remove any size information (there can be no merchant information)

        # alternatively may want to build the query using this construct in order to have max control


        # q = Q('bool',
        #     must=[Q('match', title='python')],
        #     should=[Q(...), Q(...)],
        #     minimum_should_match=1
        # )
        # s = Search().query(q)



        #################
        ### #Score Boosting
        ### https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-function-score-query.html
        # GET /_search
        # {
        #     "query": {
        #         "function_score": {
        #             "field_value_factor": {
        #                 "field": "allume_score",
        #                 "factor": 0.2,
        #                 "missing": 1
        #             }
        #         }
        #     }
        # }
        custom_score_dict = Q({'function_score': {"field_value_factor" : {"field": "allume_score", "factor": 1.5, "missing": 0}}})
        #custom_score_dict = Q('function_score', {"query" : {"match_all" : {}},"script" : "_score * (10 - doc.allume_score.doubleValue)"})
        #custom_score_dict = Q('function_score', script =  "_score * (10 - doc.allume_score.doubleValue)")
        #################
        # check for presence of the size filter AND the absence of the merchant filter
        if 'size' in self._filters and 'merchant_name' not in self._filters:
            print 'hey this happens' #?
            if self._card_count:
                return search.query(main_q).query(q_faves).query(q_available).query(q_not_deleted).query('bool', filters=[supplemental_q]).extra(collapse=collapse_dict).extra(aggs=cardinality_dict)
            else:
                return search.query(main_q).query(q_faves).query(q_available).query(q_not_deleted).query('bool', filters=[supplemental_q]).query(custom_score_dict).extra(collapse=collapse_dict).sort(self._sort)

        if self._card_count:
            return search.query(main_q).query(q_faves).query(q_available).query(q_not_deleted).extra(collapse=collapse_dict).extra(aggs=cardinality_dict)
        else:
            #search.aggs.bucket("unique_product_name_count", {"cardinality" : {"field" : "product_name.keyword"}})
            return search.query(main_q).query(q_faves).query(q_available).query(q_not_deleted).query(custom_score_dict).extra(collapse=collapse_dict).sort(self._sort)
        #.sort('-p')

def remove_deleted_items(self, days_back = 14):

    last_updated_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    print last_updated_date

