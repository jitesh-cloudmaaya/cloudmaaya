from rest_framework import serializers
from .models import StylistProfile, ClientTier
from shopping_tool.models import WpUsers

######################################
#   Serializer for add stylist API
######################################
class StylistProfileSerializer(serializers.Serializer):
    stylist_id = serializers.IntegerField()
    client_tier_id = serializers.IntegerField(required=False)
    pay_rate = serializers.FloatField(required=False)
    def create(self, validated_data, request,):
        StylistProfile.objects.create(**validated_data)