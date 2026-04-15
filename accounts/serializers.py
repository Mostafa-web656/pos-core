from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Shop, Customer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class ShopSerializer(serializers.ModelSerializer):
    owner = UserSerializer()

    class Meta:
        model = Shop
        fields = ['name', 'owner']

    def create(self, validated_data):
        owner_data = validated_data.pop('owner')
        user = User.objects.create_user(**owner_data)
        shop = Shop.objects.create(owner=user, **validated_data)
        return shop

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'phone', 'created_at']