from django.contrib import admin
from shop.models import ShopInfo, Products, Categories

class ClientsAdmin(admin.ModelAdmin):
    list_display = ('name','id')


class ProductsAdmin(admin.ModelAdmin):
    list_display = ('model','id')

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name','id')

admin.site.register(ShopInfo, ClientsAdmin)
admin.site.register(Products,ProductsAdmin)
admin.site.register(Categories,CategoryAdmin)