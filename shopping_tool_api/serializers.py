from rest_framework import serializers
from product_api.models import Product, ProductSerializer
from shopping_tool.models import LookLayout, AllumeStylingSessions, Rack, LookProduct, Look, UserProductFavorite, UserLookFavorite, AllumeClient360, LookMetrics

####################################################################################
##  REST SERIALIZERS
####################################################################################

class LookLayoutSerializer(serializers.ModelSerializer):
    #layout_json = serializers.JSONField()

    class Meta:
        model = LookLayout
        fields = ['id', 'layout_json', 'name', 'display_name', 'created_at', 'updated_at']#'__all__'

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

class LookMetricsSerializer(serializers.ModelSerializer):

    class Meta:
        model = LookMetrics
        fields = '__all__'

class LookSerializer(serializers.ModelSerializer):
    look_layout = LookLayoutSerializer(many=False, read_only=True)
    look_products = LookProductSerializer(source='product_set', many=True, read_only=True)
    look_metrics = LookMetricsSerializer(source='metric_set', many=True, read_only=True)

    class Meta:
        model = Look
        fields = '__all__'#


class LookCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Look
        fields = '__all__'#

class UserProductFavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProductFavorite
        fields = '__all__'#

class UserProductFavoriteDetailSerializer(serializers.ModelSerializer):
    product = ProductSerializer(many=False, read_only=True)

    class Meta:
        model = UserProductFavorite
        fields = '__all__'#

class UserLookFavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserLookFavorite
        fields = '__all__'#

class UserLookFavoriteDetailSerializer(serializers.ModelSerializer):
    look = LookSerializer(many=False, read_only=True)

    class Meta:
        model = UserLookFavorite
        fields = '__all__'#

class AllumeClient360Serializer(serializers.ModelSerializer):

    class Meta:
        model = AllumeClient360
        fields = '__all__'#
