from rest_framework import serializers

from auth_app.serializer import UserSerializer
from horse_app.models import Horse, SliderImage, Message


class HorseViewSerializer(serializers.ModelSerializer):
    owner = UserSerializer(many=False)
    url = serializers.HyperlinkedIdentityField('horse-detail')

    class Meta:
        model = Horse
        fields = '__all__'


class HorseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Horse
        fields = '__all__'
        read_only_fields = ['owner']


class SliderSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = SliderImage
        fields = ['id', 'image']
        read_only_fields = ['id']


class HorseSearchSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField('horse-detail')

    class Meta:
        model = Horse
        fields = ['id', 'title', 'image', 'description', 'price', 'address', 'url']


class StripeSerializer(serializers.Serializer):
    email = serializers.EmailField(allow_null=False, allow_blank=False)
    payment_method_id = serializers.CharField(max_length=200, allow_blank=False, allow_null=False)
    product_id = serializers.IntegerField()


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ['horse']