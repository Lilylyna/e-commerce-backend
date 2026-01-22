from django.contrib import admin
from .models import Category, Vendor, Product, Cart , Order

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'cid')
    search_fields = ('title', 'cid')

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('title', 'cid', 'user', 'authentic_rating')
    list_filter = ('authentic_rating',)
    search_fields = ('title', 'cid', 'user__username')
    raw_id_fields = ('user',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'pid', 'vendor', 'category', 'price', 'old_price', 'stock_count', 'status', 'date')
    list_filter = ('status', 'category', 'vendor', 'date')
    search_fields = ('title', 'pid')
    raw_id_fields = ('vendor', 'category')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'price', 'date')
    list_filter = ('date',)
    search_fields = ('user__username', 'user__email', 'product__title', 'product__pid')
    raw_id_fields = ('user', 'product')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'email', 'stripe_payment_intent', 'amount', 'currency', 'status', 'created_at')
    list_filter = ('status', 'currency', 'created_at')
    search_fields = ('id', 'user__username', 'email', 'stripe_payment_intent')
    raw_id_fields = ('user',)