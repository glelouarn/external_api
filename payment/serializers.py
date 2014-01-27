from rest_framework import serializers
from django.contrib.auth.models import User
from payment.models import Charge
from payment.models import Instrument


class InstrumentSerializer(serializers.Serializer):
    method = serializers.CharField(min_length=1, max_length=10)
    card_number = serializers.CharField(min_length=16, max_length=19)
    cvv = serializers.IntegerField(min_value=0, max_value=999)
    exp_year = serializers.IntegerField(min_value=2014, max_value=2099)
    exp_month = serializers.IntegerField(min_value=1, max_value=12)

    def restore_object(self, attrs, instance=None):
        if instance is not None:
            instance.method = attrs.get('method', instance.method)
            instance.card_number = attrs.get('card_number', instance.card_number)
            instance.cvv = attrs.get('cvv', instance.cvv)
            instance.exp_year = attrs.get('exp_year', instance.exp_year)
            instance.exp_month = attrs.get('exp_month', instance.exp_month)
            return instance
        return Instrument(**attrs)


class ChargeSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.CharField(source='url', read_only=False)
    available_methods = serializers.Field(source='methods')
    links = serializers.Field(source='construct_urls')
    messages = serializers.Field(source='messages')
    used_instruments = InstrumentSerializer(source='used_instruments', many=True, required=False)

    def save_object(self, obj, **kwargs):
        if isinstance(obj, serializers.RelationsList):
            pass
        else:
            serializers.HyperlinkedModelSerializer.save_object(self, obj, **kwargs)

    class Meta:
        model = Charge
        fields = ('id', 'status', 'messages', 'amount', 'currency', 'available_methods', 'links', 'used_instruments')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    charge = serializers.HyperlinkedRelatedField(many=True, view_name='charge-detail')

    class Meta:
        model = User
        fields = ('id', 'username', 'charges')