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

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str


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


# ------------------ RESET PASSWORD (AUTHENTICATED) ------------------ #
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reset_password_view(request):
    try:
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not old_password or not new_password:
            return Response({"error": "Old password and new password are required"},
                            status=status.HTTP_400_BAD_REQUEST)

        user = request.user

        if not user.check_password(old_password):
            return Response({"error": "Old password is incorrect"},
                            status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({"message": "Password reset successfully"},
                        status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(e)
        return Response({"error": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ------------------ FORGOT PASSWORD ------------------ #
password_reset_token = PasswordResetTokenGenerator()

@api_view(['POST'])
def forgot_password_view(request):
    email = request.data.get("email")
    if not email:
        return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

    # Basic email validation
    if '@' not in email or '.' not in email:
        return Response({"error": "Invalid email format"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Try to get user by email
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # Security: Don't reveal if user exists
        logger.info(f"Password reset requested for non-existent email: {email}")
        return Response({
            "message": "If a user exists with this email, they will receive a reset link"
        }, status=status.HTTP_200_OK)

    # Generate reset token
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = password_reset_token.make_token(user)

    reset_link = f"{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}"

    subject = "Password Reset Request"
    message = f"Hi {user.username},\n\nClick the link below to reset your password:\n{reset_link}\n\nIf you didn't request this, please ignore this email.\n\nBest regards,\nE-Commerce Team"

    try:
        # Send email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )
        
        logger.info(f"Password reset email sent successfully to {user.email}")
        
        # In development, include debug info
        if settings.DEBUG:
            return Response({
                "message": "Password reset email sent successfully",
                "debug_info": {
                    "note": "Email printed to console (development mode)",
                    "user_id": user.id,
                    "email_sent_to": user.email
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "message": "Password reset email sent successfully"
            }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")
        
        # In development, return reset link for testing
        if settings.DEBUG:
            return Response({
                "message": "Email would be sent in production. For development:",
                "reset_info": {
                    "uid": uid,
                    "token": token,
                    "reset_link": reset_link,
                    "user_id": user.id
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "error": "Failed to send email. Please try again later."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ------------------ RESET PASSWORD CONFIRM ------------------ #
@api_view(['POST'])
def reset_password_confirm_view(request):
    uid = request.data.get("uid")
    token = request.data.get("token")
    new_password = request.data.get("new_password")

    if not uid or not token or not new_password:
        return Response({"error": "uid, token, and new_password are required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=user_id)
    except (User.DoesNotExist, ValueError, TypeError):
        return Response({"error": "Invalid uid"}, status=status.HTTP_400_BAD_REQUEST)

    if not password_reset_token.check_token(user, token):
        return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save()

    return Response({"message": "Password has been reset successfully"}, status=status.HTTP_200_OK)