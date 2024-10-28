from django.db import models
from datetime import date, timedelta
import datetime as dt
import calendar, random

from account.models import *
from payme.receipts.subscribe_receipts import *

# from payment.models import *


payment = PaymeSubscribeReceipts(
    base_url =  'https://checkout.test.paycom.uz/api',
    paycom_id = '5e730e8e0b852a417aa49ceb',
    paycom_key = 'ZPDODSiTYKuX0jyO7Kl2to4rQbNwG08jbghj'
)


# Restaurant
class RestaurantQuerySet(models.QuerySet):
    
    def check_is_payment(self,user):
        get_restaurant = self.prefetch_related('author').filter(author = user).first()
        last_date_of_month = calendar.monthrange(get_restaurant.create_at.year, get_restaurant.create_at.month)[1]
        created_at = get_restaurant.create_at 
        add_one_month = created_at + timedelta(days=last_date_of_month)
        interval_of_two_dates = add_one_month - date.today()
        if (int(interval_of_two_dates.days) <= 0) or (int(interval_of_two_dates.days) > 0 and get_restaurant.is_payment == False):
            get_restaurant.price = 0
            get_restaurant.is_payment = False
            get_restaurant.save()
            return False
        return True      
            

class RestaurantManager(models.Manager):
    
    def get_queryset(self):
        return RestaurantQuerySet(self.model, using=self._db)
    
    def check_is_payment(self,user):
        return self.get_queryset().check_is_payment(user)
    
    
    
# Save Product
class SaveProductQuerySet(models.QuerySet):
    def get_product_with_author(self,user):
        for i in user.groups.all():
            if i.name == 'Servant':
               return self.prefetch_related('author').filter(author = user)                 
            return self.prefetch_related('restaurant').filter(restaurant__author = user)

    def get_by_id(self,id):
        return self.filter(id=id)
    
class SaveProductManager(models.Manager):
    
    def get_queryset(self):
        return SaveProductQuerySet(self.model, using=self._db)
    
    def get_product_with_author(self,user):
        return self.get_queryset().get_product_with_author(user)
    
    def get_by_id(self,id):
        return self.get_queryset().get_by_id(id)