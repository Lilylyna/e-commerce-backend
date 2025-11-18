from django.db import models
from shortuuid.django_fields import ShortUUIDField #install shortuuid library to use this
from django.utils.html import mark_safe #this is for admin board but not sure if ill keep it
from django.contrib.auth import get_user_model

User = get_user_model()

def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.id, filename)

# Create your models here.
class Category(models.Model):
    cid = ShortUUIDField(unique=True, length=10, max_length=30, prefix="cat", alphabet="abcdefgh12345") 
    title = models.CharField(max_length=100) #titles, headings, welcome
    image = models.ImageField(upload_to="category")


    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
    def __str__(self):
        return self.title



class Vendor(models.Model):
    cid = ShortUUIDField(unique=True, length=10, max_length=30, prefix="ven", alphabet="abcdefgh12345")
    title = models.CharField(max_length=100) #titles, headings, welcome
    image = models.ImageField(upload_to="user_directory_path")
    description = models.TextField(null=True, blank=True, max_length=500)
 
    #We can change the fields later depending on what we need
    address = models.CharField(max_length=100, default="No address found")
    contact = models.CharField(max_length=100, default="No contact found")
    chat_response_time = models.CharField(max_length=100, default="100")
    shipping_time = models.CharField(max_length=100, default="100")
    authentic_rating = models.CharField(max_length=100, default="100")
    days_return = models.CharField(max_length=100, default="100")
    warranty_period = models.CharField(max_length=100, default="100")

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)  #deleting vendors doesnt delete the shop

    class Meta:
        verbose_name = "Vendor"
        verbose_name_plural = "Vendors"
    
    def __str__(self):
        return self.title


class Product(models.Model):
    """Product model for e-commerce items"""
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('disabled', 'Disabled'),
    )
    
    pid = ShortUUIDField(unique=True, length=10, max_length=30, prefix="prod", alphabet="abcdefgh12345")
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to="products")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="products")
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, related_name="products")
    
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Original price before discount")
    
    stock_count = models.IntegerField(default=0)
    in_stock = models.BooleanField(default=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    featured = models.BooleanField(default=False)
    sku = models.CharField(max_length=100, unique=True, help_text="Stock Keeping Unit")
    
    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
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
    """Shopping cart model - stores items users want to purchase"""
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

 