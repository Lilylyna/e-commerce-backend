from django.urls import path
from userauths import views

app_name = "userauths"

urlpatterns = [
    path("sign-in/", views.sign_in_view, name="sign-in"),
    path("sign-up/", views.sign_up_view, name="sign-up"),
    path("sign-out/", views.logout_view, name="sign-out"),

    # Authenticated password reset
    path("reset-password/", views.reset_password_view, name="reset-password"),

    # Forgot password (send email)
    path("forgot-password/", views.forgot_password_view, name="forgot-password"),

    # Confirm password reset (with uid + token)
    path("reset-password-confirm/", views.reset_password_confirm_view, name="reset-password-confirm"),
]
