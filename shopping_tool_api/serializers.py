from rest_framework import serializers
from product_api.models import Product, ProductSerializer, Merchant
from shopping_tool.models import *


####################################################################################
##  REST SERIALIZERS
####################################################################################

class WpUsersNoteUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = WpUsers
        fields = ['id', 'first_name', 'last_name']
        # fields = '__all__'

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
    stylist = WpUsersNoteUserSerializer(many=False, read_only=True)

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
        fields = ['id', 'look', 'created_at','updated_at', 'product_clipped_stylist_id', 'cropped_dimensions', 'layout_position', 'product', 'in_collage', 'cropped_image_code']

class LookProductCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = LookProduct
        fields = '__all__'

class LookMetricsSerializer(serializers.ModelSerializer):

    class Meta:
        model = LookMetrics
        fields = '__all__'


class StyleTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = StyleType
        fields = ['id', 'name']

class StyleOccasionSerializer(serializers.ModelSerializer):

    class Meta:
        model = StyleOccasion
        fields = ['id', 'name']

class LookSerializer(serializers.ModelSerializer):
    look_layout = LookLayoutSerializer(many=False, read_only=True)
    look_products = LookProductSerializer(source='product_set', many=True, read_only=True)
    look_metrics = LookMetricsSerializer(source='metric_set', many=True, read_only=True)
    look_style_occasions = StyleOccasionSerializer(source='styleoccasion_set', many=True, read_only=True)
    look_style_types = StyleTypeSerializer(source='styletype_set', many=True, read_only=True)
    stylist = WpUsersNoteUserSerializer(many=False, read_only=True)

    class Meta:
        model = Look
        fields = ['id', 'token', 'allume_styling_session', 'wp_client_id', 'stylist', 'name', 'description', 'collage', 'status', 'created_at', 'updated_at', 'is_legacy', 'position', 'look_style_types', 'look_style_occasions', 'look_layout', 'look_metrics', 'look_products']

class LookSerializerNoLookProducts(serializers.ModelSerializer):
    look_layout = LookLayoutSerializer(many=False, read_only=True)
    look_metrics = LookMetricsSerializer(source='metric_set', many=True, read_only=True)
    look_style_occasions = StyleOccasionSerializer(source='styleoccasion_set', many=True, read_only=True)
    look_style_types = StyleTypeSerializer(source='styletype_set', many=True, read_only=True)
    stylist = WpUsersNoteUserSerializer(many=False, read_only=True)

    class Meta:
        model = Look
        fields = ['id', 'token', 'allume_styling_session', 'wp_client_id', 'stylist', 'name', 'description', 'collage', 'status', 'created_at', 'updated_at', 'is_legacy', 'position', 'look_style_types', 'look_style_occasions', 'look_layout', 'look_metrics']

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

class AllumeUserStylistNotesSerializer(serializers.ModelSerializer):
    stylist = WpUsersNoteUserSerializer(many=False, read_only=True)

    class Meta:
        model = AllumeUserStylistNotes
        fields = '__all__'#

class AllumeUserStylistNotesCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = AllumeUserStylistNotes
        fields = '__all__'#


######################################
#   Serializer for reporting
######################################
class AnnaReportSerializer(serializers.Serializer):
    product_id = serializers.CharField(max_length=50)
    merchant_id = serializers.CharField(max_length=50)
    reason = serializers.CharField(max_length=100)
    source = serializers.CharField(max_length=50)
    def create(self, validated_data, request):
        product = Product.objects.get(product_id = validated_data['product_id'], merchant_id = validated_data['merchant_id'])
        validated_data['product_id'] = product.id # override the product_id from merchant to our internal product id
        anna_availability = product.availability
        stylist_id = request.user.id
        Report.objects.create(stylist_id=stylist_id, anna_availability = anna_availability, **validated_data)

class ReportSerializer(serializers.Serializer):
    product_id = serializers.CharField(max_length=50)
    reason = serializers.CharField(max_length=100)
    source = serializers.CharField(max_length=50)
    def create(self, validated_data, request):
        product = Product.objects.get(id = validated_data['product_id'])
        merchant_id = product.merchant_id
        anna_availability = product.availability
        stylist_id = request.user.id
        Report.objects.create(merchant_id=merchant_id, stylist_id=stylist_id, anna_availability = anna_availability, **validated_data)


