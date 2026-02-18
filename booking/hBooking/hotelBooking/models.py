from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

User = get_user_model()


class hotelTypes(models.Model):
    hotel_id = models.AutoField(primary_key=True , db_column='hotel_id')
    hotel_type = models.CharField(max_length=255, db_column='hotel_type')
    hotel_img = models.BinaryField(db_column='hotel_img')

    class Meta:
        db_table = 'hotel_type'
        managed = True

    def __str__(self):
        return f'Product {self.hotel_id}: {self.hotel_type}'