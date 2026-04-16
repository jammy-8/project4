from django.urls import path
from . import views

urlpatterns = [
    path('', views.index , name='index'),
    path('booking/', views.booking_view, name='booking'),
    path('hotelBooking/', views.hotelBooking, name='hotelBooking'),
    path('booking_success/', views.booking_success, name='booking_success'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('edit_profile/', views.edit_profile_view, name='edit_profile'),
    path('edit_profile/update_profile', views.update_profile_view, name='update_profile'),
    path('my_bookings/', views.my_bookings, name='my_bookings'),
    path('my_bookings/update_bookings/<int:booking_id>/', views.update_booking_view, name='update_bookings'),
    path('my_booking/delete/<int:booking_id>/', views.delete_booking_view, name='delete_booking')

]
