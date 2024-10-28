from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import User,Group
from django.contrib.auth.hashers import make_password

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.exceptions import AuthenticationFailed

from account.models import *



class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class UserLoginSerializers(serializers.ModelSerializer):
    username = serializers.CharField(max_length=250)
    password = serializers.CharField(max_length=250)
    
    class Meta:
        model = User
        fields = ['username', 'password']
        

class UserPorfilesSerializers(serializers.ModelSerializer):
    groups = GroupSerializer(read_only=True, many=True)
    
    class Meta:
        model = User
        fields = ['username','groups','first_name','last_name', ]
        
        
class UserListSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','groups','first_name','last_name','password']
        
    def create(self, validated_data):
        get_role = Group.objects.filter(id = 2).first()
        create = User.objects.create(
            username = validated_data['username'],
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name'],
        )
        create.groups.add(get_role)
        create.set_password(validated_data.get('password'))
        create.save()
        restaurant = Restaurant.objects.filter(author = self.context.get("user"))[0]
        restaurant.author.add(create)
        restaurant.save()
        return create
    
    def update(self, instance, validated_data):
        instance.username = validated_data.get('username',instance.username)
        instance.first_name = validated_data.get('first_name',instance.first_name)
        instance.last_name = validated_data.get('last_name',instance.last_name)
        instance.set_password(validated_data.get('password',instance.password))
        instance.save()
        return instance 
        
        