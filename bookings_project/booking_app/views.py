from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Booking

# Create your views here.
def home(request):
    return render(request, 'home.html')

@login_required
def bookings(request):
    user_bookings = Booking.objects.filter(user=request.user)
    return render(request, 'bookings.html', {'bookings': user_bookings})