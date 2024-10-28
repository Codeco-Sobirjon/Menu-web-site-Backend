from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import User,Group
from django.contrib.auth.hashers import make_password

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.exceptions import AuthenticationFailed

from account.serializers.serializers import *
from account.models import *


class RestaurantSerializers(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = '__all__'


class CatalogListSerializers(serializers.ModelSerializer):
    class Meta:
        model = Catalog
        fields = ['id','name', 'img', 'restaurant']
    
    def create(self, validated_data):
        get_restaurant = Restaurant.objects.filter(author = self.context.get('user')).first()
        create = Catalog.objects.create(
            name = validated_data.get('name'),
            img = self.context.get('img'),
            restaurant = get_restaurant
        )
        return create
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name',instance.name)
        instance.img = validated_data.get(self.context.get('img'),self.context.get('img'))
        instance.save()
        return instance
    
class CatalogDeatilSerializers(serializers.ModelSerializer):
    restaurant = RestaurantSerializers(read_only=True)
    class Meta:
        model = Catalog
        fields = ['id','name', 'img', 'restaurant']
        
    
