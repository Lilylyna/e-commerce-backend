"""
Custom permission classes for e-commerce backend
"""
from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission:
    - Read-only for authenticated users
    - Full access for admin users
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.is_staff


class IsVendorOrReadOnly(permissions.BasePermission):
    """
    Custom permission:
    - Read-only for authenticated users
    - Full access for vendors (users with associated Vendor profile)
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # Check if user has a vendor profile
        if request.user.is_authenticated:
            from .models import Vendor
            return Vendor.objects.filter(user=request.user).exists() or request.user.is_staff
        return False


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission:
    - Users can only access their own data
    - Admins can access all data
    """
    def has_object_permission(self, request, view, obj):
        # Admins have full access
        if request.user.is_staff:
            return True
        
        # Check if object has a user attribute
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # Check if object is the user itself
        return obj == request.user


class IsVendorOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission for vendor-related objects:
    - Vendors can only access their own vendor data
    - Admins can access all vendor data
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        
        # Check if object has a vendor attribute
        if hasattr(obj, 'vendor'):
            return obj.vendor.user == request.user
        
        # If object is a Vendor itself
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Custom permission:
    - Read-only for unauthenticated users
    - Full access for authenticated users
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated

