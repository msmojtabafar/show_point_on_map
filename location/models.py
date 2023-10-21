from django.db import models


class Location(models.Model):

    name = models.CharField(max_length=50, unique=True)
    lat = models.FloatField()
    long = models.FloatField()
    time = models.TimeField()

    def __str__(self):
        return self.name
