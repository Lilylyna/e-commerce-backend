"""
Custom mixins for views with permission checks
"""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class StaffRequiredMixin(UserPassesTestMixin):
    """Mixin to require staff status"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff


class VendorRequiredMixin(UserPassesTestMixin):
    """Mixin to require vendor status"""
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        
        # Check if user is staff or has a vendor profile
        if self.request.user.is_staff:
            return True
        
        from .models import Vendor
        return Vendor.objects.filter(user=self.request.user).exists()


class OwnerOrStaffMixin(UserPassesTestMixin):
    """Mixin to allow access if user is owner or staff"""
    owner_field = 'user'  # Field name that contains the owner
    
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        
        if self.request.user.is_staff:
            return True
        
        # Get the object
        obj = self.get_object()
        owner = getattr(obj, self.owner_field, None)
        return owner == self.request.user


class VendorOwnerOrStaffMixin(UserPassesTestMixin):
    """Mixin to allow access if user owns the vendor or is staff"""
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        
        if self.request.user.is_staff:
            return True
        
        # Get the object
        obj = self.get_object()
        
        # Check if object has vendor attribute
        if hasattr(obj, 'vendor'):
            return obj.vendor.user == self.request.user
        
        # If object is Vendor itself
        if hasattr(obj, 'user'):
            return obj.user == self.request.user
        
        return False

