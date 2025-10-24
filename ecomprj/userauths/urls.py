from django.urls import path
from userauths import views 

app_name="userauths"


urlpatterns = [
    path("sign-in/", views.sign_in_view, name="sign-in"),
    path("sign-up/", views.sign_up_view, name="sign-up"),
    path("sign-out/", views.logout_view, name="sign-out"),
]