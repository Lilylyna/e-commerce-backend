from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.contrib.auth import get_user_model

User = get_user_model()

def user_directory_path(instance, filename):
    # This must be a function, not a string in the model
    return 'user_{0}/{1}'.format(instance.user.id, filename)

class Category(models.Model):
    cid = ShortUUIDField(unique=True, length=10, max_length=30, prefix="cat", alphabet="abcdefgh12345") 
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="category")

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.title

class Vendor(models.Model):
    cid = ShortUUIDField(unique=True, length=10, max_length=30, prefix="ven", alphabet="abcdefgh12345")
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to=user_directory_path) # Fixed: removed quotes
    description = models.TextField(null=True, blank=True, max_length=500)
    
    # Use OneToOneField: One user = One Store. This makes permissions much easier.
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, related_name="vendor")

    address = models.CharField(max_length=100, default="No address found")
    contact = models.CharField(max_length=100, default="No contact found")
    authentic_rating = models.CharField(max_length=100, default="100")
    chat_response_time = models.CharField(max_length=50, default="24 hours", null=True, blank=True)

    class Meta:
        verbose_name_plural = "Vendors"
    
    def __str__(self):
        return self.title

class Product(models.Model):
    pid = ShortUUIDField(unique=True, length=10, max_length=30, prefix="prod", alphabet="abcdefgh12345")
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, related_name="products")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="products")
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to="products")
    status = models.CharField(max_length=20, choices=(('draft', 'Draft'), ('published', 'Published')), default='published')
    stock_count = models.IntegerField(default=0)
    in_stock = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ['-date']
    
    def __str__(self):
        return self.title
    
    @property
    def is_discounted(self):
        """Check if product has a discount"""
        return self.old_price is not None and self.old_price > self.price
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage"""
        if self.is_discounted:
            return int(((self.old_price - self.price) / self.old_price) * 100)
        return 0

class Cart(models.Model):
    """Shopping cart model - stores items we want to purchase"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price at time of adding to cart")
    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Cart Items"
        unique_together = ['user', 'product']  # One cart entry per user per product
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user.username} - {self.product.title} x{self.quantity}"
    
    @property
    def subtotal(self):
        """Calculate subtotal for this cart item"""
        return self.price * self.quantity


class Address(models.Model):
    """User address model for shipping and billing"""
    ADDRESS_TYPE_CHOICES = [
        ('shipping', 'Shipping'),
        ('billing', 'Billing'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    address_type = models.CharField(max_length=20, choices=ADDRESS_TYPE_CHOICES, default='shipping')
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address_line_1 = models.CharField(max_length=200)
    address_line_2 = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)
    active = models.BooleanField(default=True, help_text="Soft delete flag - False means address is deleted")
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"
        ordering = ['-is_default', '-date']
    
    def __str__(self):
        return f"{self.full_name} - {self.city}, {self.state}"
    
    def soft_delete(self):
        """Soft delete the address by setting active=False"""
        self.active = False
        self.is_default = False  # Can't be default if deleted
        self.save()


class Coupon(models.Model):
    """Coupon model for discounts"""
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]
    
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, default='percentage')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_usage = models.IntegerField(default=1, help_text="Maximum number of times this coupon can be used")
    used_count = models.IntegerField(default=0)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Coupon"
        verbose_name_plural = "Coupons"
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.code} - {self.discount_value}%"
    
    def is_valid(self):
        """Check if coupon is currently valid"""
        from django.utils import timezone
        now = timezone.now()
        return (
            self.active and
            self.used_count < self.max_usage and
            self.valid_from <= now <= self.valid_to
        )
    
    def calculate_discount(self, amount):
        """Calculate discount amount based on discount type"""
        if not self.is_valid():
            return 0
        
        if self.discount_type == 'percentage':
            discount = (amount * self.discount_value) / 100
        else:  # fixed
            discount = self.discount_value
        
        # Don't allow discount to exceed the amount
        return min(discount, amount)


class Order(models.Model):
    """Order model - represents a customer order"""
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    oid = ShortUUIDField(unique=True, length=10, max_length=30, prefix="ord", alphabet="abcdefgh12345")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    
    # Price fields
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Addresses
    shipping_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, related_name="shipping_orders")
    billing_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, related_name="billing_orders")
    
    # Coupon
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    
    # Timestamps
    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ['-date']
    
    def __str__(self):
        return f"Order {self.oid} - {self.user.username} - {self.total}"
    
    def save(self, *args, **kwargs):
        """Override save to calculate total"""
        self.total = self.subtotal + self.shipping_fee + self.tax - self.discount_amount
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """Order item model - individual items in an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name="order_items")
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price at time of purchase")
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.order.oid} - {self.product.title if self.product else 'Deleted Product'} x{self.quantity}"
    
    @property
    def subtotal(self):
        """Calculate subtotal for this order item"""
        return self.price * self.quantity


