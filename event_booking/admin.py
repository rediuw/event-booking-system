from django.contrib import admin
from .models import Event, Booking, CustomUser
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'event', 'booked_on', 'tickets_booked', 'is_cancelled']
    list_filter = ['event', 'is_cancelled']
    search_fields = ['user__username', 'event__title']

class EventAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'location', 'date', 'available_tickets']
    search_fields = ['title', 'location']

admin.site.register(Event, EventAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(CustomUser)

