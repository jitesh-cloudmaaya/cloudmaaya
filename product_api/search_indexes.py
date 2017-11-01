from haystack import indexes
 
from models import Product
 
 
class ProductIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    product_name = indexes.CharField(model_attr='product_name')
    long_product_description = indexes.CharField(model_attr='long_product_description')
    short_product_description = indexes.CharField(model_attr='short_product_description')
    manufacturer_name = indexes.CharField(model_attr='manufacturer_name', faceted=True)
    manufacturer_part_number = indexes.CharField(model_attr='manufacturer_part_number')
    sku = indexes.CharField(model_attr='sku')
    product_type = indexes.CharField(model_attr='product_type', faceted=True)
    discount = indexes.DecimalField(model_attr='discount', faceted=True)
    discount_type = indexes.CharField(model_attr='discount_type', faceted=True)
    sale_price = indexes.DecimalField(model_attr='sale_price', faceted=True)
    retail_price = indexes.DecimalField(model_attr='retail_price', faceted=True) 
    shipping_price = indexes.DecimalField(model_attr='shipping_price', faceted=True) 
    color = indexes.CharField(model_attr='color', faceted=True) 
    gender = indexes.CharField(model_attr='gender', faceted=True) 
    style = indexes.CharField(model_attr='style', faceted=True) 
    size = indexes.CharField(model_attr='size', faceted=True) 
    material = indexes.CharField(model_attr='material', faceted=True) 
    age = indexes.CharField(model_attr='age', faceted=True) 
    currency = indexes.CharField(model_attr='currency', faceted=True) 
    availability = indexes.CharField(model_attr='availability', faceted=True) 
    begin_date = indexes.DateTimeField(model_attr='begin_date', faceted=True, null = True)
    end_date = indexes.DateTimeField(model_attr='end_date', faceted=True, null = True) 
    merchant_name = indexes.CharField(model_attr='merchant_name', faceted=True) 
    created_at = indexes.DateTimeField(model_attr='created_at', null = True)
    updated_at = indexes.DateTimeField(model_attr='updated_at', null = True)


 
    def get_model(self):
        return Product
 
    def index_queryset(self, using=None):
        return self.get_model().objects.all()








