from django.db import models
from shortuuid.django_fields import ShortUUIDField #install shortuuid library to use this
from django.utils.html import mark_safe #this is for admin board but not sure if ill keep it
from users.models import User

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

 