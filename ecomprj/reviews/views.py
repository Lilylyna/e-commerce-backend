from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Review
from .serializers import ReviewSerializer
from core.models import Product

class ReviewView(APIView):
  permission_classes = [IsAuthenticated]

  def post(self, request, product_id):
    product = Product.objects.get(id=product_id)
    serializer = ReviewSerializer(data=request.data)

    if serializer.is_valid():
      serializer.save(user=request.user, product=product)
      return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  def get(self, request, product_id):
    reviews = Review.objects.filter(product_id=product_id)
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)