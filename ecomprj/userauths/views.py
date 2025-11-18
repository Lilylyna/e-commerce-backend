from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
import json

User = get_user_model()

@csrf_exempt
@require_http_methods(["GET", "POST"])
def sign_in_view(request):
    """Sign in/Login view - supports both form and JSON API"""
    if request.method == 'POST':
        # Check if request is JSON
        is_json = request.content_type == 'application/json' or request.headers.get('Accept') == 'application/json'
        
        if is_json:
            try:
                data = json.loads(request.body)
                username = data.get('username')
                password = data.get('password')
            except json.JSONDecodeError:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid JSON data'
                }, status=400)
        else:
            username = request.POST.get('username')
            password = request.POST.get('password')
        
        if not username or not password:
            if is_json:
                return JsonResponse({
                    'success': False,
                    'error': 'Username and password are required'
                }, status=400)
            messages.error(request, "Username and password are required.")
            return HttpResponse("Sign In - Username and password required")
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            
            if is_json:
                return JsonResponse({
                    'success': True,
                    'message': 'Login successful',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email if hasattr(user, 'email') else None,
                    }
                }, status=200)
            
            # Redirect to home page
            return redirect('/')
        else:
            if is_json:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid username or password'
                }, status=401)
            messages.error(request, "Invalid username or password.")
            return HttpResponse("Sign In - Invalid credentials")
    
    # GET request - show sign in page
    return HttpResponse("Sign In Page - POST with username and password to login.")

@csrf_exempt
@require_http_methods(["GET", "POST"])
def sign_up_view(request):
    if request.method == 'POST':
        # Check if request is JSON
        is_json = request.content_type == 'application/json' or request.headers.get('Accept') == 'application/json'
        
        if is_json:
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({
                    'success': False,
                    'errors': {'__all__': ['Invalid JSON data']}
                }, status=400)
        else:
            data = request.POST
        
        form = UserCreationForm(data)
        if form.is_valid():
            user = form.save()
            # Automatically log in the user after signup
            login(request, user)
            messages.success(request, f"Account created successfully! Welcome, {user.username}.")
            
            # Check if request wants JSON (API call)
            if is_json:
                return JsonResponse({
                    'success': True,
                    'message': 'Account created successfully',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                    }
                }, status=201)
            
            # Redirect to home page
            return redirect('/')
        else:
            # Check if request wants JSON (API call)
            if is_json:
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)
            
            # For regular form submission, errors will be shown in template
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserCreationForm()
    
    # For GET requests or form errors, render the form
    # If you have a template, use: return render(request, 'userauths/sign_up.html', {'form': form})
    # For now, return a simple response indicating the endpoint is ready
    return HttpResponse("Sign Up Page - Form endpoint ready. POST to this URL with username, password1, password2 to create an account.")

@csrf_exempt
@require_http_methods(["GET", "POST"])
def logout_view(request):
    """Logout view - supports both form and JSON API"""
    # Check if request is JSON
    is_json = request.content_type == 'application/json' or request.headers.get('Accept') == 'application/json'
    
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "You have signed out")
        
        if is_json:
            return JsonResponse({
                'success': True,
                'message': 'Logout successful'
            }, status=200)
        
        return redirect("userauths:sign-in")
    else:
        if is_json:
            return JsonResponse({
                'success': False,
                'error': 'User is not authenticated'
            }, status=401)
        
        messages.info(request, "You are not logged in.")
        return redirect("userauths:sign-in")

