from django.db import models


# Create your models here.
class MachineOccupancyRate(models.Model):
    date = models.DateField()
    m3601 = models.FloatField()
    m1601 = models.FloatField()
    m2601 = models.FloatField()
    m1605 = models.FloatField()
    m2605 = models.FloatField()