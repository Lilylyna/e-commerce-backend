from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.utils.html import mark_safe
from .models import Category, Vendor, Product, Cart

User = get_user_model()


# Customize User Admin
# @admin.register(User)
# class CustomUserAdmin(BaseUserAdmin):
#     """Enhanced User Admin with better display and filtering"""
#     list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'is_active', 'date_joined')
#     list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
#     search_fields = ('username', 'email', 'first_name', 'last_name')
#     ordering = ('-date_joined',)
    
#     fieldsets = BaseUserAdmin.fieldsets + (
#         ('Additional Info', {
#             'fields': ('date_joined', 'last_login'),
#         }),
#     )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface for Category model"""
    list_display = ('title', 'cid', 'image_preview')
    search_fields = ('title', 'cid')
    readonly_fields = ('cid', 'image_preview')
    
    def image_preview(self, obj):
        """Display image thumbnail in admin"""
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" />')
        return "No Image"
    image_preview.short_description = "Image Preview"


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    """Admin interface for Vendor model"""
    list_display = ('title', 'cid', 'user', 'authentic_rating', 'image_preview')
    list_filter = ('authentic_rating',)
    search_fields = ('title', 'cid', 'user__username', 'user__email')
    readonly_fields = ('cid', 'image_preview')
    raw_id_fields = ('user',)  # Better for foreign key selection
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('cid', 'title', 'user', 'description', 'image')
        }),
        ('Contact Information', {
            'fields': ('address', 'contact')
        }),
        ('Performance Metrics', {
            'fields': ('chat_response_time', 'shipping_time', 'authentic_rating', 'days_return', 'warranty_period')
        }),
    )
    
    def image_preview(self, obj):
        """Display image thumbnail in admin"""
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" />')
        return "No Image"
    image_preview.short_description = "Image Preview"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin interface for Product model"""
    list_display = ('title', 'pid', 'vendor', 'category', 'price', 'old_price', 'stock_count', 'in_stock', 'status', 'featured', 'image_preview', 'date')
    list_filter = ('status', 'featured', 'in_stock', 'category', 'vendor', 'date')
    search_fields = ('title', 'pid', 'sku', 'description')
    readonly_fields = ('pid', 'image_preview', 'date', 'updated')
    raw_id_fields = ('vendor', 'category')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('pid', 'title', 'description', 'image', 'image_preview', 'sku')
        }),
        ('Pricing', {
            'fields': ('price', 'old_price')
        }),
        ('Inventory', {
            'fields': ('stock_count', 'in_stock')
        }),
        ('Relations', {
            'fields': ('category', 'vendor')
        }),
        ('Status & Visibility', {
            'fields': ('status', 'featured')
        }),
        ('Timestamps', {
            'fields': ('date', 'updated')
        }),
    )
    
    def image_preview(self, obj):
        """Display image thumbnail in admin"""
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" />')
        return "No Image"
    image_preview.short_description = "Image Preview"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin interface for Cart model"""
    list_display = ('user', 'product', 'quantity', 'price', 'subtotal_display', 'date')
    list_filter = ('date',)
    search_fields = ('user__username', 'user__email', 'product__title', 'product__sku')
    readonly_fields = ('date', 'updated', 'subtotal_display')
    raw_id_fields = ('user', 'product')
    
    fieldsets = (
        ('Cart Item', {
            'fields': ('user', 'product', 'quantity', 'price')
        }),
        ('Calculations', {
            'fields': ('subtotal_display',)
        }),
        ('Timestamps', {
            'fields': ('date', 'updated')
        }),
    )
    
    def subtotal_display(self, obj):
        """Display subtotal for cart item"""
        return f"${obj.subtotal:.2f}"
    subtotal_display.short_description = "Subtotal"
