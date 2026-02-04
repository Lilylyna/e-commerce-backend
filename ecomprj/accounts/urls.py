from django.urls import path
from .views import LoginView, ChangePasswordView, DeleteAccountView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('change-password/', ChangePasswordView.as_view()),
    path("delete-account/", DeleteAccountView.as_view()),
]