from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import User,Group
from django.contrib.auth.hashers import make_password

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.exceptions import AuthenticationFailed

from account.serializers.serializers import *
from account.models import *


class CatalogSerializers(serializers.ModelSerializer):
    class Meta:
        model = Catalog
        fields = '__all__'


class ProductListSerializers(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','name', 'img', 'price','gramms','description','catalog']
    
    def create(self, validated_data):
        get_catalog = Catalog.objects.filter(name =  validated_data.get('catalog')).first()
        create = Product.objects.create(
            name = validated_data.get('name'),
            img = self.context.get('img'),
            price = validated_data.get('price'),
            gramms = validated_data.get('gramms'),
            description = validated_data.get('description'),
            catalog = get_catalog
        )
        return create
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name',instance.name)
        instance.price = validated_data.get('price',instance.price)
        instance.gramms = validated_data.get('gramms',instance.gramms)
        instance.description = validated_data.get('description',instance.description)
        instance.img = validated_data.get(self.context.get('img'),self.context.get('img'))
        instance.save()
        return instance
    
class ProductDeatilSerializers(serializers.ModelSerializer):
    catalog = CatalogSerializers(read_only=True)
    class Meta:
        model = Product
        fields = ['id','name', 'img', 'price','gramms','description','catalog']
        
    
