from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
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
        start = request.POST.get('start_time')
        end = request.POST.get('end_time')

        Booking.objects.create(
            user=request.user,
            location=location,
            start_time=start,
            end_time=end
        )
        return redirect('bookings')  # Adjust if your bookings URL is named differently

    return render(request, 'book_details.html', {'location': location})
@login_required
def bookings(request):
    user_bookings = Booking.objects.filter(user=request.user)
    return render(request, 'bookings.html', {'bookings': user_bookings})

def logged_out(request):
    return render(request, 'logged_out.html')