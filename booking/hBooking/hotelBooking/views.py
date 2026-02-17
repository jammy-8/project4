from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def hotelBooking(request):
    return HttpResponse("This is the members page of the hotel booking app.")

def index(request):
    return render(request, 'hBooking/index.html')

def booking(request):
    return render(request, 'hBooking/booking.html')