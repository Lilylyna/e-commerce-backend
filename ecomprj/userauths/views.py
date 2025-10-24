from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.conf import settings

def sign_in_view(request):
    return HttpResponse("Sign In Page - Coming Soon!")

def sign_up_view(request):
    return HttpResponse("Sign Up Page - Coming Soon!")

def logout_view(request):
    logout(request)
    messages.success(request, "You have've signed out")
    return redirect("userauths:sign-in")

