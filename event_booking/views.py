from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, viewsets
from rest_framework.generics import ListAPIView
from rest_framework import permissions
from .models import CustomUser, Event, Booking
from .serializers import (
    UserSerializer,
    EventSerializer,
    BookingSerializer,
    UserBookingSerializer
)
from django.contrib.auth import authenticate, login, logout

# --- USER DASHBOARD ---

@login_required
def user_dashboard(request):
    current_time = timezone.now()

    upcoming_bookings = Booking.objects.filter(
        user=request.user,
        event__date__gte=current_time
    ).order_by('event__date')

    past_bookings = Booking.objects.filter(
        user=request.user,
        event__date__lt=current_time
    ).order_by('-event__date')

    # SHOW only events with tickets left and future dates
    available_events = Event.objects.filter(
        date__gte=current_time,
        available_tickets__gt=0
    )  # Removed .exclude(booking__user=request.user) for now

    return render(request, 'user_dashboard.html', {
        'upcoming_bookings': upcoming_bookings,
        'past_bookings': past_bookings,
        'available_events': available_events
    })


# --- FORM-BASED BOOKING VIEW ---
# --- EVENT DETAIL VIEW ---
@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'event_detail.html', {'event': event})

@login_required
def user_bookings(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'user_bookings.html', {'bookings': bookings})


@require_POST
@login_required
def book_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    try:
        tickets_booked = int(request.POST.get('tickets_booked', 1))
    except ValueError:
        return redirect('user_dashboard')

    if tickets_booked <= 0 or tickets_booked > event.available_tickets:
        return redirect('user_dashboard')

    Booking.objects.create(
        user=request.user,
        event=event,
        tickets_booked=tickets_booked
    )

    event.available_tickets -= tickets_booked
    event.save()

    return redirect('user_dashboard')


# --- CANCEL BOOKING API VIEW ---

class CancelBookingView(APIView):
    def post(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id, user=request.user)

            if booking.is_cancelled:
                return Response({"error": "Already cancelled"}, status=400)

            booking.is_cancelled = True
            booking.save()

            event = booking.event
            event.available_tickets += booking.tickets_booked
            event.save()

            return Response({"message": "Cancelled successfully"}, status=200)

        except Booking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=404)


# --- LOGIN, LOGOUT, REGISTER VIEWS ---

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User created!'}, status=201)
        return Response(serializer.errors, status=400)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            return redirect('user_dashboard')
        return Response({'error': 'Invalid credentials'}, status=401)


def logout_view(request):
    logout(request)
    return redirect('login')


# --- ADMIN HOMEPAGE VIEW ---

def home_view(request):
    if request.user.is_authenticated:
        events = Event.objects.filter(created_by=request.user)
        return render(request, 'home.html', {'events': events})
    return render(request, 'home.html', {'events': [], 'message': 'Please log in to view events.'})


# --- API Views (optional for mobile/frontend)

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class BookEventView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, event_id):
        event = Event.objects.get(id=event_id)
        tickets_booked = int(request.data.get('tickets_booked', 1))

        if tickets_booked > event.available_tickets:
            return Response({'error': 'Not enough tickets'}, status=400)

        booking = Booking.objects.create(
            user=request.user,
            event=event,
            tickets_booked=tickets_booked
        )
        event.available_tickets -= tickets_booked
        event.save()

        serializer = BookingSerializer(booking)
        return Response(serializer.data, status=201)

class UserBookingsView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserBookingSerializer

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)
