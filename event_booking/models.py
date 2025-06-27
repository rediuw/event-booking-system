from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class CustomUser(AbstractUser):
    is_admin = models.BooleanField(default=False)  # True for admins, False for regular users

    def __str__(self):
        return self.username  # Helps in debugging when printing user objects

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=255)
    date = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available_tickets = models.IntegerField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title


class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    booked_on = models.DateTimeField(auto_now_add=True)
    tickets_booked = models.IntegerField()
    is_cancelled = models.BooleanField(default=False)  # New field to track cancellation status

    def __str__(self):
        return f"Booking for {self.event.title} by {self.user.username}"

