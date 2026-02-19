from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

# User = get_user_model()

class hotelTypes(models.Model):
    hotel_id = models.AutoField(primary_key=True , db_column='hotel_id')
    hotel_type = models.CharField(max_length=255, db_column='hotel_type')
    hotel_img = models.ImageField(db_column='hotel_img')

    class Meta:
        db_table = 'hotel_type'
        managed = True

    def __str__(self):
        return f'Product {self.hotel_id}: {self.hotel_type}'


class booking(models.Model):
    booking_id = models.AutoField(primary_key=True, db_column='booking_id')
    first_name = models.CharField(max_length=255, db_column='first_name')
    last_name = models.CharField(max_length=255, db_column='last_name')
    email = models.EmailField(db_column='email')
    phone_number = models.CharField(max_length=20, db_column='phone_number')
    check_in_date = models.DateField(db_column='check_in_date')
    check_out_date = models.DateField(db_column='check_out_date')
    hotel_type = models.ForeignKey(hotelTypes, db_column='hotel_type', on_delete=models.CASCADE)

    class Meta:
        db_table = 'booking'
        managed = True

    def __str__(self):
        return f'Booking {self.booking_id} for {self.first_name} {self.last_name} at {self.hotel_type} on {self.check_in_date} to {self.check_out_date}'