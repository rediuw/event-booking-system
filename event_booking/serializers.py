from django.contrib.auth.models import User
from rest_framework import serializers
from .models import CustomUser, Event
from rest_framework import serializers
from .models import Booking

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'email']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user



class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'location', 'date', 'price', 'available_tickets']


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'user', 'event', 'booked_on', 'tickets_booked']
        read_only_fields = ['booked_on']
        
class UserBookingSerializer(serializers.ModelSerializer):
    event = EventSerializer()

    class Meta:
        model = Booking
        fields = ['id', 'event', 'tickets_booked', 'booked_on']
