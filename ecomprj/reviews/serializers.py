from rest_framework import serializers
from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
  user = serializers.ReadOnlyField(source='user.username')

  class Meta:
    model = Review
    fields = ['id', 'user', 'rating', 'comment']