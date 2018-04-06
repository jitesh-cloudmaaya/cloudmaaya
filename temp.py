# this is a temp file for writing the one time script to run to exclude/'flag as deleted' existing products
# AND set their corresponding category_map allume_category_id = 10 (EXCLUDE), active = 0, and pending_review = 0

from product_api.models import Product, CategoryMap, OtherTermMap, AllumeCategory
# from product_api.models import SynonymCategoryMap
from django.db.models import Q

# STEP 1: perform a search on product name in the products table and check if the product name contains any words
# present under the 'Other' category on the shared spreadsheet of terms

terms = OtherTermMap.objects.values_list('term', flat=True)
queries = [Q(product_name__icontains=term) for term in terms]

query = queries.pop()

for item in queries:
    query |= item

category_pairs = Product.objects.filter(query).values_list('primary_category', 'secondary_category').distinct()


# STEP 2: Find the corresponding categorymap entries
ALLUME_CATEGORY_OTHER = AllumeCategory.objects.get(name='Other')
for category_pair in category_pairs:
    categorymap = CategoryMap.objects.get(external_cat1 = category_pair[0], external_cat2 = category_pair[1])
    if not categorymap.allume_category or categorymap.allume_category.name == 'Unsure':
        # STEP 3A: update the categorymap secondary category and allume_category_id to 'Other', active = 1, pending = 0

        # both of these steps might duplicate, so I should handle that fact
        categorymap.external_cat2 = 'Other'
        categorymap.allume_category = ALLUME_CATEGORY_OTHER
        categorymap.turned_on = True
        categorymap.pending_review = False
        
        # handle in the event that this creates a duplicate...


    else:
        # STEP 3B: Duplicate the category_map
        duplicated_categorymap = CategoryMap(external_cat1 = categorymap.external_cat1)
        # update the secondary_category and allume_category_id to 'Other', active = 1, and pending = 0,
        duplicated_categorymap.external_cat2 = 'Other'
        duplicated_categorymap.allume_category = ALLUME_CATEGORY_OTHER
        duplicated_categorymap.turned_on = True
        duplicated_categorymap.pending_review = False
        # this might already exist...
        # update product secondary_category to 'Other'
        pass

# categorymaps = CategoryMap.objects.filter()