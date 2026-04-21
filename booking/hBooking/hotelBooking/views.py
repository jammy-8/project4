from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import models
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
import base64
from io import BytesIO
from .forms import CustomUserCreationForm, ProfileForm
from .models import booking, hotelTypes, User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import  authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from datetime import datetime
from django.utils import timezone

try:
    from PIL import Image
    _PIL_AVAILABLE = True
except Exception:
    Image = None
    _PIL_AVAILABLE = False

def _process_image(binary, max_width=640, max_height=480):
    """Return a data URL for the image, resizing it if larger than the provided dimensions.
    If Pillow is not available, returns the original image as base64 if possible."""
    if not binary:
        return None
    try:
        if not _PIL_AVAILABLE:
            return 'data:image/png;base64,' + base64.b64encode(binary).decode('ascii')
        img = Image.open(BytesIO(binary))
        # Convert to RGB/RGBA to avoid mode issues when saving
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA")
        w, h = img.size
        if w > max_width or h > max_height:
            try:
                resample = Image.Resampling.LANCZOS
            except AttributeError:
                resample = Image.ANTIALIAS
            img.thumbnail((max_width, max_height), resample)
        out = BytesIO()
        img.save(out, format='PNG')
        out.seek(0)
        return 'data:image/png;base64,' + base64.b64encode(out.read()).decode('ascii')
    except Exception:
        # Fallback to returning the raw image if something goes wrong
        try:
            return 'data:image/png;base64,' + base64.b64encode(binary).decode('ascii')
        except Exception:
            return None


def hotelBooking(request):
    return HttpResponse("This is the members page of the hotel booking app.")

def index(request):
    hTypesObj = hotelTypes.objects.all()
    hotelTypesList = []
    for hType in hTypesObj:
        hotelTypesList.append({
            'hotel_id': hType.hotel_id,
            'hotel_type': hType.hotel_type,
            'hotel_img': hType.hotel_img
        })
    return render(request, 'hBooking/index.html', {'hotelTypesList': hotelTypesList})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.POST.get('next') or request.GET.get('next') or 'index'
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'hBooking/login.html')

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(request, username=username, password=raw_password)
            # login(request, user)
            messages.success(request, 'Account created successfully.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()

    return render(request, 'hBooking/signup.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('index')

@login_required
def booking_view(request):
    hotel_types = hotelTypes.objects.all()

    if request.method == 'POST':
        check_in_date = request.POST.get('check-in')
        check_out_date = request.POST.get('check-out')
        hotel_type_id = request.POST.get('room')

        hotel_type = hotelTypes.objects.get(hotel_id=hotel_type_id)

        booking.objects.create(
            user = request.user,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            hotel_type=hotel_type
        )

        return redirect('booking_success')
    
    return render(request, 'hBooking/booking.html', {'hotel_types': hotel_types})

def booking_success(request):
    return render(request, 'hBooking/booking_success.html')


def edit_profile_view(request):
    form = ProfileForm(instance=request.user)
    password_form = PasswordChangeForm(request.user)
    return render(request, 'hBooking/edit_profile.html', {'form' : form, 'password_form': password_form})

def update_profile_view(request):
    user = request.user
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        password_form = PasswordChangeForm(request.user, request.POST)

        password_field_filled = (
            request.POST.get('old_password') or
            request.POST.get('new_password1') or
            request.POST.get('new_password2')
        )

        if form.is_valid():
            # user = form.save(commit=False)
            form.save()

            if password_field_filled:
                if password_form.is_valid():

                    user = password_form.save()
                    update_session_auth_hash(request, user)

                    messages.success(request, 'Profile has been updated', extra_tags='profile')
                else:
                    messages.error(request, "Please correct errors", extra_tags='profile')
            
                    return redirect('edit_profile')
                
            else: 
                messages.success(request, 'Profile has been updated', extra_tags='profile')
        
        else:
            messages.error(request, "Please correct errors in profile", extra_tags='profile')

    return redirect('edit_profile')

def my_bookings(request):
    user_bookings = booking.objects.filter(user=request.user)
    return render(request, 'hBooking/my_bookings.html', {
        'bookings': user_bookings,
        'hotel_types': hotelTypes
    })

def update_booking_view(request, booking_id):
    booking_obj = get_object_or_404(booking, booking_id=booking_id, user=request.user)
    hotel_types = hotelTypes.objects.all()
    today = timezone.now().date()

    if request.method == 'POST':
        temp_check_in_date = request.POST.get('check-in')
        temp_check_out_date = request.POST.get('check-out')

        check_in_date = datetime.strptime(temp_check_in_date, "%Y-%m-%d").date()
        check_out_date = datetime.strptime(temp_check_out_date, "%Y-%m-%d").date()
   

        if check_in_date < today:
            messages.error(request, "Check-in date Invalid", extra_tags='booking_create')
            return render(request, 'hBooking/booking.html', {
                'booking': booking_obj,
                'hotel_types': hotel_types,
                'today': today
            }) 
        
        if check_out_date <= check_in_date:
            messages.error(request, "Check-out should be after Check-in", extra_tags='booking_create')
            return render(request, 'hBooking/booking.html', {
                'booking': booking_obj,
                'hotel_types': hotel_types,
                'today': today
            }) 
        
        booking_obj.check_in_date = check_in_date
        booking_obj.check_out_date = check_out_date

        hotel_type_id = request.POST.get('room')
        booking_obj.hotel_type = hotelTypes.objects.get(hotel_id=hotel_type_id)

        booking_obj.save()

        messages.success(request, "Booking has been updated", extra_tags='booking')
        return redirect('my_bookings')
    
    return render(request, 'hBooking/booking.html', {
        'booking': booking_obj,
        'hotel_types': hotel_types,
        'today': today
    })

def delete_booking_view(request, booking_id):
    booking_obj = get_object_or_404(booking, booking_id=booking_id, user=request.user)

    if request.method == 'POST':
        booking_obj.delete()
        messages.success(request, "Booking deleted successfully",  extra_tags='booking')
        return redirect('my_bookings')

    return redirect('my_bookings')

