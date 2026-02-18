from django.shortcuts import render
from django.db import models
from django.http import HttpResponse
import base64
from io import BytesIO
from .models import hotelTypes

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
        img = _process_image(hType.hotel_img, max_width=200, max_height=200)
        hotelTypesList.append({
            'hotel_id': hType.hotel_id,
            'hotel_type': hType.hotel_type,
            'hotel_img': img
        })
    return render(request, 'hBooking/index.html', {'hotelTypesList': hotelTypesList})

def booking(request):
    return render(request, 'hBooking/booking.html')