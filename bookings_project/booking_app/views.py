from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import datetime

from .models import Booking, Location

# Create your views here.
def home(request):
    return render(request, 'home.html')

@login_required
def book(request):
    if request.method == 'POST':
        location_id = request.POST.get('location_id')


        location = get_object_or_404(Location, id=location_id)

        Booking.objects.create(
            user=request.user,
            location=location,

        )
        return redirect('book')

    locations = Location.objects.all()
    return render(request, 'book.html', {'locations': locations})

@login_required
def book_details(request, number):
    location = get_object_or_404(Location, number=number)

    if request.method == 'POST':
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        if not start_time or not end_time:
            messages.error(request, "Both start and end times are required.")
            return redirect('book_details', number=number)

        start_time = timezone.make_aware(datetime.fromisoformat(start_time))
        end_time = timezone.make_aware(datetime.fromisoformat(end_time))

        # ❗ Check for overlapping bookings
        conflicts = Booking.objects.filter(
            location=location,
            start_time__lt=end_time,
            end_time__gt=start_time
        )

        if conflicts.exists():
            messages.error(request, "This room is already booked in that time range.")
            return redirect('book_details', number=number)

        # If no conflicts, save the booking
        Booking.objects.create(
            user=request.user,
            location=location,
            start_time=start_time,
            end_time=end_time,
        )

        messages.success(request, "Room booked successfully!")
        return redirect('bookings')

    return render(request, 'book_details.html', {'location': location})

@login_required
def bookings(request):
    user_bookings = Booking.objects.filter(user=request.user)
    return render(request, 'bookings.html', {'bookings': user_bookings})

def logged_out(request):
    return render(request, 'logged_out.html')

@require_POST
def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    password = request.POST.get('password')

    user = authenticate(username=request.user.username, password=password)
    if user:
        booking.delete()
        messages.success(request, "Booking deleted successfully.")
    else:
        messages.error(request, "Incorrect password. Booking not deleted.")
    return redirect('bookings')