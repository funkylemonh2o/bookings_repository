from django.contrib import admin
from .models import Booking, Location, Feedback

# Register your models here.
admin.site.register(Location)
admin.site.register(Booking)
admin.site.register(Feedback)