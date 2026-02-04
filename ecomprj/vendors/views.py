from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from core.models import Vendor, Product

# Si OrderItem existe
try:
  from core.models import OrderItem
  ORDERS_ENABLED = True
except ImportError:
  ORDERS_ENABLED = False


class VendorDashboardView(APIView):
  permission_classes = [IsAuthenticated]

  def get(self, request):
    vendor = get_object_or_404(Vendor, user=request.user)

    products = Product.objects.filter(vendor=vendor)

    data = {
      "total_products": products.count(),
      "products": [
        {
          "id": p.id,
          "title": p.title,
          "price": p.price
        }
        for p in products
      ],
      "total_sales": 0,
      "total_revenue": 0
    }

    if ORDERS_ENABLED:
      order_items = OrderItem.objects.filter(
        product__vendor=vendor
      )

      data["total_sales"] = order_items.aggregate(
        total=Sum('quantity')
      )['total'] or 0

      data["total_revenue"] = order_items.aggregate(
        total=Sum('price')
      )['total'] or 0

    return Response(data)
