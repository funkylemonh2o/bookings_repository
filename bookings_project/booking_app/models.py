from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Location(models.Model):
    number = models.IntegerField()
    capacity = models.IntegerField()
    location = models.TextField()
    def __str__(self):
        return f"Room #{self.number} - {self.capacity}"

    class Meta:
        verbose_name = "Location"
        verbose_name_plural = "Locations"
        ordering = ["number"]



class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="bookings")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    creation_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.location}"

    class Meta:
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"
        ordering = ["start_time"]

