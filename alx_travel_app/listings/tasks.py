from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_confirmation_email(user_email, tx_ref):
    """Background task to send payment confirmation."""
    subject = f'Booking Confirmed - Ref: {tx_ref}'
    message = f'Your payment for transaction {tx_ref} was successful. Thank you!'
    send_mail(subject, message, 'noreply@yourdomain.com', [user_email])


@shared_task(bind=True, max_retries=3)
def send_booking_confirmation_email(self, booking_id):
    """
    Send booking confirmation email asynchronously.
    Args:
        booking_id (int): ID of the booking to send confirmation for
    """
    try:
        from .models import Booking
        
        # Get booking instance
        booking = Booking.objects.select_related('listing', 'user').get(id=booking_id)
        
        # Prepare email content
        subject = f'Booking Confirmation #{booking.booking_number}'
        
        context = {
            'booking': booking,
            'listing': booking.listing,
            'user': booking.user,
            'check_in': booking.check_in_date,
            'check_out': booking.check_out_date,
            'total_price': booking.total_price,
            'guests': booking.number_of_guests,
            'booking_number': booking.booking_number,
        }
        
        # Render HTML and plain text versions
        html_message = render_to_string('listings/emails/booking_confirmation.html', context)
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Booking confirmation email sent for booking #{booking.booking_number}")
        
        # Update booking status if needed
        if not booking.confirmation_sent:
            booking.confirmation_sent = True
            booking.save(update_fields=['confirmation_sent'])
        
        return f"Email sent successfully for booking #{booking.booking_number}"
        
    except Booking.DoesNotExist:
        logger.error(f"Booking with id {booking_id} does not exist")
        return f"Booking with id {booking_id} not found"
        
    except Exception as e:
        logger.error(f"Failed to send booking confirmation email: {e}")
        # Retry the task after 60 seconds
        raise self.retry(exc=e, countdown=60)
# listings/tasks.py (additional tasks)
@shared_task
def check_pending_bookings():
    """
    Check for pending bookings and send reminders
    """
    from .models import Booking
    from datetime import datetime, timedelta
    
    # Find bookings pending for more than 24 hours
    time_threshold = datetime.now() - timedelta(hours=24)
    pending_bookings = Booking.objects.filter(
        status='pending',
        created_at__lt=time_threshold
    )
    
    for booking in pending_bookings:
        send_booking_reminder_email.delay(booking.id)
    
    return f"Checked {pending_bookings.count()} pending bookings"

@shared_task
def send_booking_reminders():
    """
    Send reminder emails for upcoming bookings
    """
    from .models import Booking
    from datetime import datetime, timedelta
    
    # Find bookings starting in the next 48 hours
    reminder_date = datetime.now() + timedelta(hours=48)
    upcoming_bookings = Booking.objects.filter(
        status='confirmed',
        check_in_date__lte=reminder_date.date(),
        check_in_date__gt=datetime.now().date()
    )
    
    for booking in upcoming_bookings:
        send_upcoming_booking_reminder.delay(booking.id)
    
    return f"Sent reminders for {upcoming_bookings.count()} upcoming bookings"

@shared_task
def send_booking_reminder_email(booking_id):
    """
    Send reminder for pending booking
    """
    # Similar to send_booking_confirmation_email
    pass

@shared_task
def send_upcoming_booking_reminder(booking_id):
    """
    Send reminder for upcoming booking
    """
    # Similar to send_booking_confirmation_email
    pass
