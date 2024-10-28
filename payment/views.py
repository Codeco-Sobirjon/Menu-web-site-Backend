from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render,redirect
from django.contrib.auth.models import *
from datetime import date, timedelta

from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework import generics, permissions, status, views
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from account.renderers import *
from account.models import *
from payment.models import *
from payment.payme.cards import *
from payment.payme.receipts import *

from payme.receipts.subscribe_receipts import PaymeSubscribeReceipts

import random

payment = PaymeSubscribeReceipts(
    base_url = 'https://checkout.paycom.uz/api',
    paycom_id = '64a7e800a58caefa2d34e657',
    paycom_key = 'c2UiZh8Um8kjgtTV32h76MZpcXw8M0qj%7Nm'
)



class VirifyCardView(APIView):
    render_classes = [UserRenderers]
    permission_classes = [IsAuthenticated]
    
    def post(self,request,format=None):
        token = request.data['token']
        phone = request.data['phone']
        get_restaurant = Restaurant.objects.prefetch_related('author').filter(author = request.user).first()
        create = Order.objects.create(
            token = token,
            phone = phone,
            restaurant = get_restaurant
        )
        return Response({'msg':create.unique_id},status = status.HTTP_201_CREATED)


class Payment(APIView):
    render_classes = [UserRenderers]
    permission_classes = [IsAuthenticated]
    
    def post(self,request,unique_id,format=None):
        get_token = get_object_or_404(Order,unique_id=unique_id)
        amount = request.data['amount']  
        order_id = random.randint(1, 999)
        receipt_create_credential =  payment.receipts_create(amount=int(amount), order_id=order_id)
        receipt_pay_credential = payment.receipts_pay(invoice_id=receipt_create_credential['result']['receipt']['_id'], token=get_token.token, phone=get_token.phone)
        restaurant = Restaurant.objects.prefetch_related('author').filter(author = request.user).update(create_at = date.today(),is_payment=True,price=int(amount))
        return Response({'data':'Success'},status=status.HTTP_200_OK)
