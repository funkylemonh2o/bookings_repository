from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import datetime
from .forms import  RegisterForm
from .models import Booking, Location, Feedback
from django.core.mail import send_mail

from bookings.settings import EMAIL_HOST_USER


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

        # ✅ Create booking
        booking = Booking.objects.create(
            user=request.user,
            location=location,
            start_time=start_time,
            end_time=end_time,
        )

        # ✅ Send email confirmation
        subject = "Booking Confirmation"
        message = f"""
        Hi {request.user.username},

        Your booking for {location.number} is confirmed.

        📅 Start: {booking.start_time.strftime('%Y-%m-%d %H:%M')}
        📅 End: {booking.end_time.strftime('%Y-%m-%d %H:%M')}

        Thanks for booking with us!
        """
        email = request.user.email
        if not email:
            messages.error(request, "Your account doesn't have an email address set.")
            return redirect('book_details', number=number)

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [email],  # <-- now guaranteed not None
            fail_silently=False,
        )
        messages.success(request, "Room booked successfully! Confirmation sent via email.")
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




@login_required
def feedback(request):
    rooms = Location.objects.all()

    if request.method == 'POST':
        room_id = request.POST.get('room')
        comment = request.POST.get('comment', '')
        room = Location.objects.get(id=room_id)

        has_booking = Booking.objects.filter(user=request.user, location=room).exists()

        if not has_booking:
            comment = ''  # Strip comment if no booking
            rating = 5    # Force 5-star rating
        else:
            rating = int(request.POST.get('rating'))

        Feedback.objects.create(user=request.user, location=room, rating=rating, comment=comment)
        messages.success(request, 'Thank you for your feedback!')
        return redirect('home')

    return render(request, 'feedback.html', {'rooms': rooms})
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Optional: auto-login after registration
            return redirect('home')  # Change 'home' to your desired redirect
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def send_booking_confirmation(user, booking):
    subject = "Booking Confirmation"
    message = f"""
    Hi {user.username},

    Your booking at {booking.location} has been confirmed.

    Start Time: {booking.start_time}
    End Time: {booking.end_time}

    Thank you for using our service!

    - Booking System
    """
    recipient = user.email
    send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient])

def confirm_booking(request, booking_id, token):
    """
    This view is what the user hits when they click
    https://<your-domain>/confirmation/<booking_id>/<token>/.
    We verify the token, mark the booking as confirmed, and then show a “thanks” page.
    """
    booking = get_object_or_404(Booking, id=booking_id, booking_token=token)

    # Token matches—mark booking as confirmed and clear the token so it can’t be reused:
    booking.is_confirmed = True
    booking.booking_token = ""
    booking.save()

    return render(request, 'bookings/booking_confirmed.html', {
        'booking': booking
    })
