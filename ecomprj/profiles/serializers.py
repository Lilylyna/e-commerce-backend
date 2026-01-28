from rest_framework import serializers
from .models import Profile
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['username', 'email']


class ProfileSerializer(serializers.ModelSerializer):
  class Meta:
    model = Profile
    fields = ['bio', 'phone', 'image']