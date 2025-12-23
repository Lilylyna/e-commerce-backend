from django.contrib.auth.mixins import UserPassesTestMixin
from .models import Vendor

class VendorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        # Simplified: Check if user has a vendor attribute linked to them
        return hasattr(self.request.user, 'vendor') or self.request.user.is_staff

class VendorOwnerOrStaffMixin(UserPassesTestMixin):
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        if self.request.user.is_staff:
            return True
        
        obj = self.get_object()
        # If the object is a product, check if the product's vendor belongs to the user
        if hasattr(obj, 'vendor'):
            return obj.vendor.user == self.request.user
        # If the object is the Vendor itself
        if isinstance(obj, Vendor):
            return obj.user == self.request.user
        return False

