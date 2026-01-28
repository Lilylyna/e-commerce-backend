from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
  user = models.OneToOneField(
    User,
    on_delete=models.CASCADE,
    related_name='profile'
  )
  bio = models.TextField(blank=True)
  phone = models.CharField(max_length=10, blank=True)
  image = models.ImageField(upload_to='profiles/', blank=True, null=True)

  def __str__(self):
    return self.user.username