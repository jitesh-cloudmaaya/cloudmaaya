from rest_framework import serializers
from product_api.models import Product, ProductSerializer
from shopping_tool.models import LookLayout, AllumeStylingSessions, Rack, LookProduct, Look

####################################################################################
##  REST SERIALIZERS
####################################################################################

class LookLayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = LookLayout
        fields = '__all__'

class AllumeStylingSessionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AllumeStylingSessions

class RackSerializer(serializers.ModelSerializer):
    product = ProductSerializer(many=False, read_only=True)

    class Meta:
        model = Rack
        fields = '__all__'

class RackCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rack
        fields = '__all__'

class LookProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(many=False, read_only=True)

    class Meta:
        model = LookProduct
        fields = '__all__'

class LookProductCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = LookProduct
        fields = '__all__'


class LookSerializer(serializers.ModelSerializer):
    look_layout = LookLayoutSerializer(many=False)
    look_products = LookProductSerializer(source='product_set', many=True, read_only=True)

    class Meta:
        model = Look
        fields = '__all__'#

class LookCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Look
        fields = '__all__'#
