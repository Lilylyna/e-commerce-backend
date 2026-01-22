from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import logout

import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Order


stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.
def index(request): 
    return HttpResponse("welcome to our store!")


#when testing api replace the above with the syntax commented out
#from django.http import JsonResponse

#def index(request):
   # return JsonResponse({"message": "Welcome to the backend API"})

