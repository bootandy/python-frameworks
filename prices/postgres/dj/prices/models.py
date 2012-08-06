from django.db import models

# Create your models here.

class HousePrice(models.Model):
    description = models.CharField(max_length=200)
    address = models.CharField(max_length=100)
    postcode_part = models.CharField(max_length=10)
    dateadded = models.DateTimeField('date published')
    price = models.IntegerField()
    