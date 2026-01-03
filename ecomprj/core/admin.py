from django.contrib import admin
from .models import Category, Vendor, Product, Cart, Address, Coupon, Order, OrderItem

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


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'address_type', 'city', 'state', 'country', 'is_default', 'active', 'date')
    list_filter = ('address_type', 'country', 'is_default', 'active', 'date')
    search_fields = ('full_name', 'user__username', 'user__email', 'city', 'state', 'zip_code')
    raw_id_fields = ('user',)
    list_editable = ('active',)  # Allow quick toggle of active status


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'minimum_purchase', 'used_count', 'max_usage', 'active', 'valid_from', 'valid_to')
    list_filter = ('discount_type', 'active', 'valid_from', 'valid_to')
    search_fields = ('code',)
    readonly_fields = ('used_count', 'date')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user',)  # Removed invalid fields
    list_filter = ()  # Removed invalid fields
    search_fields = ('user__username', 'user__email')
    readonly_fields = ()  # Removed invalid fields
    raw_id_fields = ('user',)  # Removed invalid fields

    fieldsets = (
        ('Order Information', {
            'fields': ('user',)
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')  # Removed invalid fields
    list_filter = ()  # Removed invalid fields
    search_fields = ('order__user__username', 'product__title')
    raw_id_fields = ('order',)  # Removed invalid fields


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('product', 'quantity', 'price')  # Removed invalid fields
