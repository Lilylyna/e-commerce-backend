from django.urls import path
from . import views

urlpatterns = [
    path('start_payment/', views.start_payment, name='start_payment'),
    path('payment_detail/<int:pk>/', views.payment_detail, name='payment_detail'),
]