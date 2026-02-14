from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Listing, Booking
from .serializers import ListingSerializer, BookingSerializer

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def perform_create(self, serializer):
        serializer.save(host=self.request.user)
    
    def get_queryset(self):
        queryset = Listing.objects.all()
        
        # Filter by availability
        available_only = self.request.query_params.get('available', None)
        if available_only and available_only.lower() == 'true':
            queryset = queryset.filter(is_available=True)
        
        # Filter by property type
        property_type = self.request.query_params.get('property_type', None)
        if property_type:
            queryset = queryset.filter(property_type=property_type)
        
        # Filter by max price
        max_price = self.request.query_params.get('max_price', None)
        if max_price:
            queryset = queryset.filter(price_per_night__lte=max_price)
        
        # Filter by minimum bedrooms
        min_bedrooms = self.request.query_params.get('min_bedrooms', None)
        if min_bedrooms:
            queryset = queryset.filter(bedrooms__gte=min_bedrooms)
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def bookings(self, request, pk=None):
        listing = self.get_object()
        bookings = listing.bookings.all()
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # Users can see their own bookings and bookings for their listings
        if user.is_authenticated:
            return Booking.objects.filter(
                Q(guest=user) | Q(listing__host=user)
            ).distinct()
        return Booking.objects.none()
    
    def perform_create(self, serializer):
        listing = serializer.validated_data['listing']
        
        # Calculate total price
        nights = (serializer.validated_data['check_out'] - serializer.validated_data['check_in']).days
        total_price = nights * listing.price_per_night
        
        serializer.save(
            guest=self.request.user,
            total_price=total_price
        )
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        booking = self.get_object()
        
        # Only listing host can confirm bookings
        if booking.listing.host != request.user:
            return Response(
                {'error': 'Only the listing host can confirm bookings.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        booking.status = 'confirmed'
        booking.save()
        
        serializer = self.get_serializer(booking)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        
        # Only guest or host can cancel
        if booking.guest != request.user and booking.listing.host != request.user:
            return Response(
                {'error': 'Only the guest or host can cancel this booking.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        booking.status = 'cancelled'
        booking.save()
        
        serializer = self.get_serializer(booking)
        return Response(serializer.data)
