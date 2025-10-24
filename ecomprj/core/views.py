from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import logout

# Create your views here.
def index(request): 
    return HttpResponse("welcome to our store!")


#when testing api replace the above with the syntax commented out
#from django.http import JsonResponse

#def index(request):
   # return JsonResponse({"message": "Welcome to the backend API"})
