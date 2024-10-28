from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render,redirect
from django.contrib.auth.models import *
from datetime import date, timedelta
from django.db.models import Q

from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework import generics, permissions, status, views
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import filters

from account.serializers.serializers import *
from account.serializers.res_serializers import *
from account.serializers.product_serializers import *
from account.serializers.product_save_serializers import *
from account.renderers import *
from account.models import *

import jsonschema,random
from jsonschema import Draft7Validator
from payme.receipts.subscribe_receipts import *


from environs import Env

import os
import sys

from dotenv import load_dotenv
load_dotenv()

env = Env()
env.read_env()


payment = PaymeSubscribeReceipts(
    base_url = 'https://checkout.paycom.uz/api',
    paycom_id = '64a7e800a58caefa2d34e657',
    paycom_key = 'c2UiZh8Um8kjgtTV32h76MZpcXw8M0qj%7Nm'
)


def get_token_for_user(user):
    
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access':str(refresh.access_token)
    }


class UserLoginView(APIView):
    render_classes = [UserRenderers]
    
    def post(self,request,format=None):
        serializers = UserLoginSerializers(data=request.data, partial=True)
        if serializers.is_valid(raise_exception=True):
            username = serializers.data['username']
            password = serializers.data['password']
            token = ''
            if username=='' and password=='':
                return Response({'error':{'none_filed_error':['Username or password is not write']}},status=status.HTTP_204_NO_CONTENT)
            user = authenticate(username=username, password=password)    
            if user is None:
                return Response({'error':{'none_filed_error':['Username or password is not valid']}},status=status.HTTP_404_NOT_FOUND)
            elif len(user.groups.all().filter(name='Servant')) != 0:
                is_pay = "Servant"
                token = get_token_for_user(user)
                return Response({'token':token,'message':serializers.data,'is_payment':is_pay,},status=status.HTTP_200_OK)
            else:
                token = get_token_for_user(user)
                get_user_restaurant = Restaurant.objects.prefetch_related('author').filter(author = user)[0]
                get_restaurant = Restaurant.objects.check_is_payment(user)
                check_token_in_order = Order.objects.filter(restaurant__author=user).first()
                print(get_restaurant)
                print(check_token_in_order)
                if get_restaurant:
                    print(1)
                    is_pay = "Payed"
                    token = get_token_for_user(user)
                    return Response({'token':token,'message':serializers.data,'is_payment':is_pay,'price':get_user_restaurant.price},status=status.HTTP_200_OK)
                elif check_token_in_order == None:
                    print(2)
                    is_pay = "NeverPaid"
                    token = get_token_for_user(user)
                    get_user_restaurant.price = 0
                    get_user_restaurant.is_payment = False
                    get_user_restaurant.save()
                    return Response({'token':token,'message':serializers.data,'is_payment':is_pay,'price':get_user_restaurant.price},status=status.HTTP_200_OK)
                else:
                    print(3)
                    amount = 150000
                    order_id = random.randint(1, 999)
                    receipt_create_credential =  payment.receipts_create(amount=int(amount), order_id = order_id)
                    receipt_pay_credential = payment.receipts_pay(invoice_id=receipt_create_credential['result']['receipt']['_id'], token=check_token_in_order.token, phone=check_token_in_order.phone)
                    print(receipt_pay_credential)
                    if receipt_pay_credential['error']['code'] == -31630:
                        print(4)
                        is_pay = "IsNotPayed"
                        get_user_restaurant.price = 0
                        get_user_restaurant.is_payment = False
                        get_user_restaurant.save()
                    else:
                        print(5)
                        is_pay = "Payed"
                        get_user_restaurant.price = amount
                        get_user_restaurant.is_payment = True
                        get_user_restaurant.create_at = date.today()
                        get_user_restaurant.save()

                return Response({'token':token,'message':serializers.data,'is_payment':is_pay,'price':get_user_restaurant.price},status=status.HTTP_200_OK)
        return Response(serializers.errors,status=status.HTTP_400_BAD_REQUEST)
    

class UserProfilesView(APIView):
    render_classes = [UserRenderers]
    permission_classes = [IsAuthenticated]
    
    def get(self,request,format=None):
        serializer = UserPorfilesSerializers(request.user)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    
class UserLogoutView(APIView):
    permission_classes  = [IsAuthenticated]
    render_classes = [UserRenderers]
    
    def post(self, request):
        tokens = OutstandingToken.objects.filter(user_id=request.user.id)
        for token in tokens:
            t, _ = BlacklistedToken.objects.get_or_create(token=token)

        return Response(status=status.HTTP_205_RESET_CONTENT)
    
    
class RestaurantView(APIView):
    render_classes = [UserRenderers]
    permission_classes = [IsAuthenticated]
    
    def get(self,request,format=None):
        res = Restaurant.objects.filter(author = request.user)
        serializers = RestaurantSerializers(res,many=True)
        return Response(serializers.data,status=status.HTTP_200_OK)    

#CATALOG
class CatalogListViews(APIView):
    render_classes = [UserRenderers]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, format=None):
        catalogs = Catalog.objects.prefetch_related('restaurant').filter(restaurant__author = request.user).order_by('-id')
        serializers = CatalogDeatilSerializers(catalogs,many=True)
        return Response(serializers.data,status=status.HTTP_200_OK)
    
    def post(self,request,format=None):
        serializers = CatalogListSerializers(data=request.data,context={'img':request.FILES.get('img',None),'user':request.user})
        if serializers.is_valid(raise_exception=True):
            serializers.save()
            return Response(serializers.data,status=status.HTTP_200_OK)
        return Response(serializers.errors,status=status.HTTP_400_BAD_REQUEST)
    

class CatalogDetailViews(APIView):
    render_classes = [UserRenderers]
    permission_classes = [IsAuthenticated]
    
    def get(self,request,id, format=None):
        queryset = get_object_or_404(Catalog,id=id)
        serializers = CatalogDeatilSerializers(queryset)
        return Response(serializers.data,status=status.HTTP_200_OK)
    
    def put(self,request,id,format=None):
        queryset = get_object_or_404(Catalog,id=id)
        serializers = CatalogDeatilSerializers(instance=queryset, data=request.data, partial=True, context={'img':request.FILES.get('img',None)})
        if serializers.is_valid(raise_exception=True):
            serializers.save()
            return Response(serializers.data,status=status.HTTP_200_OK)
        return Response(serializers.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request,id,format=None):
        queryset = get_object_or_404(Catalog,id=id)
        queryset.delete()
        return Response({'message':'deleted successfully'},status=status.HTTP_200_OK)
    
# PRODUCT   
class ProductListViews(APIView):
    render_classes = [UserRenderers]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, format=None):
        products = Product.objects.prefetch_related('catalog').filter(catalog__restaurant__author = request.user).order_by('-id')
        serializers = ProductDeatilSerializers(products,many=True)
        return Response(serializers.data,status=status.HTTP_200_OK)
    
    def post(self,request,format=None):
        serializers = ProductListSerializers(data=request.data,context={'img':request.FILES.get('img',None),'user':request.user})
        if serializers.is_valid(raise_exception=True):
            serializers.save()
            return Response(serializers.data,status=status.HTTP_201_CREATED)
        return Response(serializers.errors,status=status.HTTP_400_BAD_REQUEST)


class ProductFilterView(generics.ListAPIView):
    render_classes = [UserRenderers]
    permission_classes = [IsAuthenticated]
    queryset = Product.objects.all()
    serializer_class = ProductDeatilSerializers
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name',]
    
    def get(self, request, format=None):
        search_name = request.query_params.get('search_name', '')
        product = Product.objects.filter((Q(name__icontains=search_name)))
        serializers = self.serializer_class(product, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)
    
    
class ProductDetailViews(APIView):
    render_classes = [UserRenderers]
    permission_classes = [IsAuthenticated]
    
    def get(self,request,id, format=None):
        queryset = get_object_or_404(Product,id=id)
        serializers = ProductDeatilSerializers(queryset)
        return Response(serializers.data,status=status.HTTP_200_OK)
    
    def put(self,request,id,format=None):
        queryset = get_object_or_404(Product,id=id)
        serializers = ProductDeatilSerializers(instance=queryset, data=request.data, partial=True, context={'img':request.FILES.get('img',None)})
        if serializers.is_valid(raise_exception=True):
            serializers.save()
            return Response(serializers.data,status=status.HTTP_200_OK)
        return Response(serializers.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request,id,format=None):
        queryset = get_object_or_404(Product,id=id)
        queryset.delete()
        return Response({'message':'deleted successfully'},status=status.HTTP_200_OK)
    
    
#Servant
class CustomUserListViews(APIView):
    render_classes = [UserRenderers]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, format=None):
        servants = User.objects.filter(groups__name__in = ['Servant'])
        restaurant = [Restaurant.objects.prefetch_related('author').filter(author = i).values('author__first_name','author__last_name','author__username','author__id') for i in servants ]
        return Response(restaurant)
    
    
    def post(self,request,format=None):
        serializers = UserListSerializers(data=request.data,context={'user':request.user})
        if serializers.is_valid(raise_exception=True):
            serializers.save()
            return Response(serializers.data,status=status.HTTP_201_CREATED)
        return Response(serializers.errors,status=status.HTTP_400_BAD_REQUEST)
    

class CustomUserDetailViews(APIView):
    render_classes = [UserRenderers]
    permission_classes = [IsAuthenticated]
    
    def get(self,request,id, format=None):
        queryset = get_object_or_404(User,id=id)
        serializers = UserPorfilesSerializers(queryset)
        return Response(serializers.data,status=status.HTTP_200_OK)
    
    def put(self,request,id,format=None):
        queryset = get_object_or_404(User,id=id)
        serializers = UserListSerializers(instance=queryset, data=request.data, partial=True)
        if serializers.is_valid(raise_exception=True):
            serializers.save()
            return Response(serializers.data,status=status.HTTP_200_OK)
        return Response(serializers.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request,id,format=None):
        queryset = get_object_or_404(User,id=id)
        queryset.delete()
        return Response({'message':'deleted successfully'},status=status.HTTP_200_OK)
    
    
class ProductSaveView(APIView):
    render_classes = [UserRenderers]
    permission_classes = [IsAuthenticated]
    
    def get(self,request,format=None):
        save_product  = SaveOrder.obj.get_product_with_author(request.user).order_by('-id')
        serializers = ProductSaveListSerializers(save_product,many=True)
        return Response(serializers.data,status=status.HTTP_200_OK)
    
    
    def post(self,request,format=None):
        restaurant = Restaurant.objects.filter(author = request.user)[0]
        serializer = ProductSave(data=request.data,context={'user':request.user})
        if serializer.is_valid(raise_exception=True):
            serializer.save(files = request.FILES.get('files',None),restaurant=restaurant)
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)  
    
    

class ProductSaveFilterView(generics.ListAPIView):
    render_classes = [UserRenderers]
    permission_classes = [IsAuthenticated]
    queryset = SaveOrder.obj.all()
    serializer_class = ProductSaveListSerializers
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['full_name','phone']
    


class ProductSaveDetailsView(APIView):
    render_classes = [UserRenderers]
    permission_classes = [IsAuthenticated]
    
    def get(self,request,id,format=None):
        save_product  = get_object_or_404(SaveOrder,id=id)
        serializers = ProductSaveListSerializers(save_product)
        return Response(serializers.data,status=status.HTTP_200_OK)
    
    def put(self,request,id,format=None):
        get_by_id = get_object_or_404(SaveOrder,id=id)
        serializer=ProductSave(instance=get_by_id,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save(files = request.FILES.get('files',None))
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request,id,format=None):
        get_by_id = get_object_or_404(SaveOrder,id=id).delete()
        return Response({'message':'deleted successfully'},status=status.HTTP_200_OK)
    
    
class CatalogProductView(APIView):
    render_classes = [UserRenderers]
    permission_classes = [IsAuthenticated]
    
    def get(self,request,id,format=None):
        get_catalog = get_object_or_404(Catalog,id=id)
        products = Product.objects.prefetch_related('catalog').filter(catalog = get_catalog.id,catalog__restaurant__author = request.user )
        serializers = ProductDeatilSerializers(products,many=True)
        return Response(serializers.data,status=status.HTTP_200_OK)