from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from listings.models import Listing, Booking, Review
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Seed the database with sample listings, bookings, and reviews'
    
    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')
        
        # Clear existing data
        Review.objects.all().delete()
        Booking.objects.all().delete()
        Listing.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        
        # Create sample users
        users = []
        for i in range(1, 6):
            user = User.objects.create_user(
                username=f'user{i}',
                email=f'user{i}@example.com',
                password='password123',
                first_name=f'First{i}',
                last_name=f'Last{i}'
            )
            users.append(user)
            self.stdout.write(f'Created user: {user.username}')
        
        # Create sample listings
        listings_data = [
            {
                'title': 'Cozy Apartment in Downtown',
                'description': 'A beautiful apartment in the heart of the city',
                'address': '123 Main St, Downtown, City',
                'property_type': 'apartment',
                'price_per_night': 120.00,
                'max_guests': 4,
                'bedrooms': 2,
                'bathrooms': 1,
                'amenities': 'WiFi, Kitchen, TV, Air Conditioning'
            },
            {
                'title': 'Luxury Villa with Pool',
                'description': 'Stunning villa with private pool and ocean view',
                'address': '456 Beach Rd, Coastal Area',
                'property_type': 'villa',
                'price_per_night': 350.00,
                'max_guests': 8,
                'bedrooms': 4,
                'bathrooms': 3,
                'amenities': 'Pool, WiFi, Kitchen, TV, Air Conditioning, Parking'
            },
            {
                'title': 'Modern Condo Near Airport',
                'description': 'Convenient condo perfect for business travelers',
                'address': '789 Airport Blvd, Business District',
                'property_type': 'condo',
                'price_per_night': 85.00,
                'max_guests': 2,
                'bedrooms': 1,
                'bathrooms': 1,
                'amenities': 'WiFi, Kitchen, TV, Gym Access'
            },
            {
                'title': 'Spacious Family House',
                'description': 'Perfect for family vacations with large garden',
                'address': '321 Garden St, Suburban Area',
                'property_type': 'house',
                'price_per_night': 200.00,
                'max_guests': 6,
                'bedrooms': 3,
                'bathrooms': 2,
                'amenities': 'Garden, WiFi, Kitchen, TV, Parking'
            }
        ]
        
        listings = []
        for data in listings_data:
            listing = Listing.objects.create(
                host=random.choice(users),
                **data
            )
            listings.append(listing)
            self.stdout.write(f'Created listing: {listing.title}')
        
        # Create sample bookings
        statuses = ['pending', 'confirmed', 'completed', 'cancelled']
        for i in range(10):
            listing = random.choice(listings)
            guest = random.choice([u for u in users if u != listing.host])
            
            check_in = datetime.now().date() + timedelta(days=random.randint(1, 30))
            check_out = check_in + timedelta(days=random.randint(1, 14))
            nights = (check_out - check_in).days
            total_price = nights * float(listing.price_per_night)
            
            booking = Booking.objects.create(
                listing=listing,
                guest=guest,
                check_in=check_in,
                check_out=check_out,
                total_price=total_price,
                status=random.choice(statuses),
                guests_count=random.randint(1, listing.max_guests),
                special_requests='Early check-in requested' if random.choice([True, False]) else ''
            )
            
            # Create review for completed bookings
            if booking.status == 'completed' and random.choice([True, False]):
                Review.objects.create(
                    booking=booking,
                    rating=random.randint(3, 5),
                    comment='Great stay! Would recommend.'
                )
            
            self.stdout.write(f'Created booking for: {listing.title}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully seeded database with sample data!')
        )
