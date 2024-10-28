from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import User,Group
from django.contrib.auth.hashers import make_password

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.exceptions import AuthenticationFailed

from account.serializers.res_serializers import *
from account.models import *
from account.serializers.serializers import *

import json


class ProductSave(serializers.ModelSerializer):
    full_name = serializers.CharField(max_length=10,required=False)
    class Meta:
        model = SaveOrder
        fields = ('id','full_name','phone','detailed_data','comment','files','restaurant')
        
    def create(self, validated_data):
        create = SaveOrder.obj.create(**validated_data)
        create.author = self.context.get('user')
        create.save()
        return create
    
    def update(self, instance, validated_data):
        instance.full_name = validated_data.get('full_name',instance.full_name)
        instance.phone = validated_data.get('phone',instance.phone)
        instance.detailed_data = validated_data.get('detailed_data',instance.detailed_data)
        instance.comment = validated_data.get('comment',instance.comment)
        instance.save()
        return instance
    
    
class ProductSaveListSerializers(serializers.ModelSerializer):
    restaurant = RestaurantSerializers(read_only=True)
    author = UserPorfilesSerializers(read_only=True)
    class Meta:
        model = SaveOrder
        fields = ['id','full_name','phone','detailed_data','comment','files','restaurant','author']