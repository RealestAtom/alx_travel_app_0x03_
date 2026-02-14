from rest_framework import serializers
from .models import Listing, Booking, Review
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class ListingSerializer(serializers.ModelSerializer):
    host = UserSerializer(read_only=True)
    
    class Meta:
        model = Listing
        fields = [
            'id', 'title', 'description', 'address', 'property_type',
            'price_per_night', 'max_guests', 'bedrooms', 'bathrooms',
            'amenities', 'host', 'is_available', 'created_at', 'updated_at'
        ]
        read_only_fields = ['host', 'created_at', 'updated_at']

class BookingSerializer(serializers.ModelSerializer):
    listing = ListingSerializer(read_only=True)
    guest = UserSerializer(read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'listing', 'guest', 'check_in', 'check_out',
            'total_price', 'status', 'guests_count', 'special_requests',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['guest', 'created_at', 'updated_at']

class ReviewSerializer(serializers.ModelSerializer):
    booking = BookingSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'booking', 'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
