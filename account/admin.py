from django.contrib import admin
from account.models import *


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name','id','price','create_at')


@admin.register(Catalog)
class CatalogAdmin(admin.ModelAdmin):
    list_display = ('name','id','restaurant')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name','id','price','gramms','catalog')


@admin.register(SaveOrder)
class SaveProductAdmin(admin.ModelAdmin):
    list_display = ('full_name','id','phone')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('token','restaurant','unique_id')