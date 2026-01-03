from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def sign_up_view(request):
    if request.method == 'POST':
        try:
            # Parse JSON data
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                logger.error("Invalid JSON data", exc_info=True)
                return JsonResponse({'error': 'Invalid JSON data'}, status=400)

            # Extract fields
            username = data.get('username')
            password1 = data.get('password1')
            password2 = data.get('password2')

            # Validate fields
            if not username or not password1 or not password2:
                return JsonResponse({'error': 'All fields are required'}, status=400)

            if password1 != password2:
                return JsonResponse({'error': 'Passwords do not match'}, status=400)

            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username already exists'}, status=400)

            # Create user
            user = User.objects.create_user(username=username, password=password1)
            user.save()

            logger.info(f"User {username} registered successfully.")
            return JsonResponse({'message': 'User registered successfully'}, status=201)

        except Exception as e:
            logger.error("Unexpected error in sign_up_view", exc_info=True)
            return JsonResponse({'error': 'An unexpected error occurred. Please try again later.'}, status=500)

    return JsonResponse({'error': 'Invalid HTTP method'}, status=405)

def sign_in_view(request):
    return HttpResponse("Sign In Page - Coming Soon!")

def logout_view(request):
    logout(request)
    messages.success(request, "You have've signed out")
    return redirect("userauths:sign-in")

