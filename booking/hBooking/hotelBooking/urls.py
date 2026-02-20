from django.urls import path
from . import views

urlpatterns = [
    path('', views.index , name='index'),
    path('booking', views.booking_view, name='booking'),
    path('hotelBooking', views.hotelBooking, name='hotelBooking'),
    path('booking_success', views.booking_success, name='booking_success'),
]
