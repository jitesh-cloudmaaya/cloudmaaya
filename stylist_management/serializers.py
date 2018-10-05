from rest_framework import serializers
from .models import StylistProfile, ClientTier
from shopping_tool.models import WpUsers
from django.utils import timezone

######################################
#   Serializer for add stylist API
######################################
class StylistProfileSerializer(serializers.Serializer):
    stylist_id = serializers.IntegerField()
    client_tier_id = serializers.IntegerField(required=False)
    pay_rate = serializers.FloatField(required=False)
    role_id = serializers.CharField(required=False)
    director_id = serializers.IntegerField(required=False)
    manager_id = serializers.IntegerField(required=False)
    asm_id = serializers.IntegerField(required=False)
    birthday = serializers.DateTimeField(required=False)

    def create(self, validated_data):
        StylistProfile.objects.create(**validated_data)

    def off_board(self, validated_data):
        stylist = StylistProfile.objects.get(stylist_id = validated_data['stylist_id'])
        stylist.on_board = False
        stylist.off_board_date = timezone.now()
        stylist.save()

