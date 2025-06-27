from django.contrib import admin
from django.shortcuts import render
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    home_view,
    logout_view,
    LoginView,
    RegisterView,
    user_dashboard,
    event_detail,
    user_bookings,
    book_event,                   # <-- HTML form booking view
    BookEventView,                # <-- API booking view
    CancelBookingView,
    UserBookingsView,
    EventViewSet
)

# DRF router for /api/events/
router = DefaultRouter()
router.register(r'events', EventViewSet)

urlpatterns = [
    # 🌐 Public home
    path('', home_view, name='home'),

    # 🔐 Auth
    path('admin/', admin.site.urls),
    path('logout/', logout_view, name='logout'),
    path('accounts/login/', LoginView.as_view(), name='login'),
    path('accounts/register/', RegisterView.as_view(), name='register'),

    # 📄 HTML-based user system
    path('dashboard/', user_dashboard, name='user_dashboard'),
    path('event/<int:event_id>/', event_detail, name='event_detail'),
    path('user/bookings/', user_bookings, name='user_bookings'),
    path('events/<int:event_id>/book/', book_event, name='book_event'),  # <== FORM booking

    # 🔌 API endpoints
    path('api/', include(router.urls)),
    path('api/events/<int:event_id>/book/', BookEventView.as_view(), name='api_book_event'),
    path('api/user/bookings/', UserBookingsView.as_view(), name='api_user_bookings'),
    path('api/bookings/<int:booking_id>/cancel/', CancelBookingView.as_view(), name='api_cancel_booking'),

    # 🔐 JWT Auth API
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
