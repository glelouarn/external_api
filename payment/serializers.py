from rest_framework import serializers
from django.contrib.auth.models import User
from payment.models import Charge


class ChargeSerializer(serializers.HyperlinkedModelSerializer):
    available_methods = serializers.Field(source='methods')
    used_instruments = serializers.Field(source='instruments')
    links = serializers.Field(source='construct_urls')
    messages = serializers.Field(source='messages')

    class Meta:
        model = Charge
        fields = ('id', 'status', 'messages', 'amount', 'currency', 'available_methods', 'used_instruments', 'links')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    charge = serializers.HyperlinkedRelatedField(many=True, view_name='charge-detail')

    class Meta:
        model = User
        fields = ('id', 'username', 'charges')