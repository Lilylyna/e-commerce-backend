from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request): 
    return HttpResponse("welcome to our store!")

#when testing api replace the above with the syntax commented out
#from django.http import JsonResponse

#def index(request):
   # return JsonResponse({"message": "Welcome to the backend API"})
