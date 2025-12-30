from django.urls import path
from .views import ReviewView

urlpatterns = [
  path('product/<int:product_id>/', ReviewView.as_view()),
]
