from django.db import models

# Create your models here.
from django_mongodb_engine.contrib import MongoDBManager

class HousePrice(models.Model):
    class Meta:
      db_table = 'houses'

    objects = MongoDBManager()

    address = models.TextField()
    description = models.TextField()
    dateadded = models.DateField()
    price =  models.IntegerField()
    postcode_part = models.TextField()

