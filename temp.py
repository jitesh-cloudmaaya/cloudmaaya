# this is a temp file for writing the one time script to run to exclude/'flag as deleted' existing products
# AND set their corresponding category_map allume_category_id = 10 (EXCLUDE), active = 0, and pending_review = 0

from product_api.models import Product, CategoryMap, AllumeCategory, SynonymCategoryMap
from django.db.models import Q

# STEP 1: perform a search on product name in the products table and check if the product name contains any words
# present under the 'Other' category on the shared spreadsheet of terms

terms = SynonymCategoryMap.objects.filter(category = 'Other').values_list('synonym', flat=True)
queries = [Q(product_name__icontains=term) for term in terms]

query = queries.pop()

for item in queries:
    query |= item

# define the total set of products that qualify
products = Product.objects.filter(query)
category_pairs = products.values_list('primary_category', 'secondary_category').distinct()


# STEP 2: Find the corresponding categorymap entries
ALLUME_CATEGORY_OTHER = AllumeCategory.objects.get(name='Other')
for category_pair in category_pairs:
    categorymap = CategoryMap.objects.get(external_cat1 = category_pair[0], external_cat2 = category_pair[1])
    if not categorymap.allume_category or categorymap.allume_category.name == 'Unsure':
        # STEP 3A: update the categorymap secondary category and allume_category_id to 'Other', active = 1, pending = 0

        # in the event of a duplicate, I should delete one of the duplicate CategoryMap objects
        categorymap.external_cat2 = 'Other'

        # search for duplicates here?
        try:
            # if this call resolves, there was indeed a duplicate
            duplicate_categorymap = CategoryMap.objects.get(external_cat1 = categorymap.external_cat1, external_cat2 = categorymap.external_cat2)

            # so we should delete the duplicate entry (either the one being changed to or the one already in place)
            categorymap.delete()

            # and then update the older already in place duplicate to be this replacement
            categorymap = duplicate_categorymap

        except CategoryMap.DoesNotExist:
            # no duplicate at the altered set of categories exists
            pass

        categorymap.allume_category = ALLUME_CATEGORY_OTHER
        categorymap.turned_on = True
        categorymap.pending_review = False

        categorymap.save()


    else:
        # STEP 3B: Duplicate the category_map

        # store the original categories of the categorymap in variables in order to do the update....
        # or do it earlier actually
        # update the products' secondary category to 'Other'
        products_to_update = products.filter(primary_category=categorymap.external_cat1, secondary_category=categorymap.external_cat2)

        # perform a bulk update on these products, chaning their secondary category to 'Other'

        # rationale for using for loop of save rather than django update
        # queryset.update() does not update datetime auto_now fields, which only update during save
        # as some tasks/jobs depend on checking the product's updated_at field, this is undesirable
        # a custom updated_at could be used during the update, but seemed a bit wanting
        for product in products_to_update:
            product.secondary_category = 'Other'
            product.save()

        # this might already exist... we should update one and delete the other
        # update product secondary_category to 'Other'
        categorymap.external_cat2 = 'Other'

        try:
            # if this call resolves, there was indeed a duplicate
            duplicate_categorymap = CategoryMap.objects.get(external_cat1 = categorymap.external_cat1, external_cat2 = categorymap.external_cat2)

            # so we should delete the duplicate entry (either the one being changed to or the one already in place)
            categorymap.delete()

            # and then update the older already in place duplicate to be this replacement
            categorymap = duplicate_categorymap

        except CategoryMap.DoesNotExist:
            # no duplicate at the altered set of categories exists
            pass

        categorymap.allume_category = ALLUME_CATEGORY_OTHER
        categorymap.turned_on = True
        categorymap.pending_review = False

        categorymap.save()



        # we can only know what product's have what primary and secondary categories
        # is it possible that we will heavily rewrite something based on these updated categories

# categorymaps = CategoryMap.objects.filter()



# try refactoring