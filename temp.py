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
    if categorymap.allume_category and categorymap.allume_category != 'Unsure':
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


# this is take 2, dependent on whether Pamela agrees with this formation
from product_api.models import Product, CategoryMap, AllumeCategory, SynonymCategoryMap
from django.db.models import Q

# maybe try and reimplement in this direction
# steps of this process as I newly understand it

# we should find the list of products that have a term that maps to 'Other' in their product name...
terms = SynonymCategoryMap.objects.filter(category = 'Other').values_list('synonym', flat=True)
queries = [Q(product_name__icontains=term) for term in terms]

query = queries.pop()

for item in queries:
    query |= item

# define the total set of products that qualify
products = Product.objects.filter(query)
# keep set of old category pairs on hand to use for updating the CategoryMaps
category_pairs = products.values_list('primary_category', 'secondary_category').distinct()
# don't use update because that doesn't trigger save() or auto_now
for product in products:
# always update these products such that they have a secondary category of 'Other'
# and an allume cat of 'Other' (because this is what the catmap will change to)
    product.secondary_category = 'Other'
    proudct.allume_category = 'Other'
    product.save()

for category_pair in category_pairs:
    primary_category = category_pair[0]
    # for use in getting the merchant name...
    base_secondary_category = category_pair[1]
    secondary_category = 'Other'

    # then we should either create, if a catmap of that pair does not exist, or update, if it does, the category maps
    # such that there is one that reflects these changes to product name
    # aka catmap = external_cat1, 'Other', allume_category of Other, active = 1, pending_review = 0
    try:
        # create
        categorymap = CategoryMap.objects.get(external_cat1 = primary_category, external_cat2 = secondary_category)
    except CategoryMap.DoesNotExist:
        # update
        try:
            base_categorymap = CategoryMap.objects.get(external_cat1 = primary_category, external_cat2 = base_secondary_category)
        except CategoryMap.DoesNotExist as e:
            print e
            print 'The CategoryMap at these categories should exist. It is advisable to investigate why this is occurring.'
        categorymap = CategoryMap(external_cat1 = primary_category, merchant_name = base_categorymap.merchant_name)
    categorymap.external_cat2 = 'Other'
    categorymap.allume_category = AllumeCategory.objects.get(name='Other')
    categorymap.turned_on = True
    categorymap.pending_review = False
    categorymap.save()

