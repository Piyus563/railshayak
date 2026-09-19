import razorpay
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Booking
from .serializers import BookingSerializer
from .whatsapp import (
    notify_booking_created, notify_booking_accepted,
    notify_booking_started, notify_booking_completed,
    notify_booking_cancelled, notify_booking_rejected
)
from accounts.models import CoolieProfile, User
from stations.models import Station, Platform
from reviews.models import Review
from notifications.models import Notification


def _razorpay_client():
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def _amount_in_paise(amount):
    return int(Decimal(amount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) * 100)


# --- HTML Views ---

@login_required
def book_coolie_view(request):
    """Create a booking and send the passenger to payment."""
    stations = Station.objects.filter(is_active=True)
    selected_station_code = request.GET.get('station', 'NJP')
    station = Station.objects.filter(code__iexact=selected_station_code).first() or stations.first()
    platforms = station.platforms.all() if station else []
    available_coolies = CoolieProfile.objects.filter(station=station, is_verified=True, is_online=True)

    if request.method == 'POST':
        station_id = request.POST.get('station_id')
        platform_id = request.POST.get('platform_id')
        coolie_id = request.POST.get('coolie_id')
        journey_type = request.POST.get('journey_type', 'ARRIVAL')
        train_number = request.POST.get('train_number', '').strip()
        train_name = request.POST.get('train_name', '').strip()
        coach_number = request.POST.get('coach_number', '').strip()
        seat_number = request.POST.get('seat_number', '').strip()
        luggage_type = request.POST.get('luggage_type', 'TROLLEY')
        number_of_bags = int(request.POST.get('number_of_bags', 1))
        approx_weight_kg = int(request.POST.get('approx_weight_kg', 20))
        meeting_point = request.POST.get('meeting_point', '').strip()
        special_notes = request.POST.get('special_notes', '').strip()
        scheduled_date = request.POST.get('scheduled_date', '').strip()
        scheduled_clock = request.POST.get('scheduled_clock', '').strip()
        scheduled_time_raw = f'{scheduled_date}T{scheduled_clock}' if scheduled_date and scheduled_clock else ''

        scheduled_time = timezone.now()
        if scheduled_time_raw:
            try:
                scheduled_time = datetime.fromisoformat(scheduled_time_raw)
                if timezone.is_naive(scheduled_time):
                    scheduled_time = timezone.make_aware(scheduled_time)
            except ValueError:
                messages.error(request, 'Please enter a valid booking date and time.')
                return redirect('bookings:book_coolie')

        stn_obj = get_object_or_404(Station, id=station_id)
        plat_obj = Platform.objects.filter(id=platform_id).first() if platform_id else None
        coolie_obj = CoolieProfile.objects.filter(id=coolie_id).first() if coolie_id else available_coolies.first()

        booking = Booking(
            passenger=request.user,
            coolie=coolie_obj,
            station=stn_obj,
            platform=plat_obj,
            journey_type=journey_type,
            train_number=train_number,
            train_name=train_name,
            coach_number=coach_number,
            seat_number=seat_number,
            luggage_type=luggage_type,
            number_of_bags=number_of_bags,
            approx_weight_kg=approx_weight_kg,
            meeting_point=meeting_point or f"Platform {plat_obj.number if plat_obj else '1'} Main Gate",
            special_notes=special_notes,
            scheduled_time=scheduled_time,
            status='REQUESTED',
            payment_status='PENDING',
        )
        booking.calculate_fare()
        booking.save()

        # Redirect to payment page instead of directly confirming
        return redirect('bookings:payment', booking_id=booking.booking_id)

    context = {
        'stations': stations,
        'current_station': station,
        'platforms': platforms,
        'available_coolies': available_coolies,
    }
    return render(request, 'bookings/book_coolie.html', context)


@login_required
def payment_page_view(request, booking_id):
    """Show the payment page; order creation happens through create_payment_view."""
    booking = get_object_or_404(Booking, booking_id=booking_id, passenger=request.user)

    # Prevent re-payment if already paid
    if booking.payment_status == 'PAID':
        return redirect('bookings:payment_success', booking_id=booking.booking_id)

    razorpay_configured = bool(settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET)

    context = {
        'booking': booking,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'amount_paise': _amount_in_paise(booking.total_fare),
        'razorpay_configured': razorpay_configured,
        'passenger_name': request.user.get_full_name() or request.user.username,
        'passenger_email': request.user.email or '',
        'passenger_phone': request.user.phone or '',
    }
    return render(request, 'bookings/payment.html', context)


@login_required
@require_POST
def create_payment_view(request, booking_id):
    """Create one server-side Razorpay order for a pending booking."""
    booking = get_object_or_404(Booking, booking_id=booking_id, passenger=request.user)
    if booking.payment_status == 'PAID':
        return JsonResponse({'status': 'already_paid', 'redirect': reverse('bookings:payment_success', args=[booking.booking_id])})
    if booking.status == 'CANCELLED':
        return JsonResponse({'status': 'failed', 'message': 'This booking is cancelled.'}, status=400)
    if not (settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET):
        return JsonResponse({'status': 'failed', 'message': 'Payment gateway is not configured.'}, status=503)

    # The amount is always recalculated from the booking, never accepted from the browser.
    booking.calculate_fare()
    amount_paise = _amount_in_paise(booking.total_fare)
    if (booking.payment_status == 'PENDING' and booking.razorpay_order_id and
            booking.payment_amount == booking.total_fare):
        return JsonResponse({'status': 'created', 'order_id': booking.razorpay_order_id, 'amount': amount_paise})

    try:
        order = _razorpay_client().order.create({
            'amount': amount_paise,
            'currency': 'INR',
            'receipt': booking.booking_id,
            'notes': {'booking_id': booking.booking_id, 'station': booking.station.code},
        })
    except Exception:
        return JsonResponse({'status': 'failed', 'message': 'Unable to start payment. Please try again.'}, status=502)

    booking.razorpay_order_id = order['id']
    booking.payment_amount = booking.total_fare
    booking.save(update_fields=['total_fare', 'base_fare', 'extra_bag_fare', 'razorpay_order_id', 'payment_amount', 'updated_at'])
    return JsonResponse({'status': 'created', 'order_id': order['id'], 'amount': amount_paise})


@login_required
@require_POST
def verify_payment_view(request, booking_id):
    """Verify Razorpay payment signature on backend — NEVER trust frontend."""
    booking = get_object_or_404(Booking, booking_id=booking_id, passenger=request.user)

    if booking.payment_status == 'PAID':
        return JsonResponse({'status': 'already_paid', 'redirect': f'/bookings/payment-success/{booking.booking_id}/'})

    razorpay_order_id = request.POST.get('razorpay_order_id', '')
    razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
    razorpay_signature = request.POST.get('razorpay_signature', '')

    # Validate all fields present
    if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
        booking.payment_status = 'FAILED'
        booking.save(update_fields=['payment_status'])
        return JsonResponse({'status': 'failed', 'message': 'Missing payment fields'}, status=400)

    # Verify order_id matches what we stored
    if razorpay_order_id != booking.razorpay_order_id:
        booking.payment_status = 'FAILED'
        booking.save(update_fields=['payment_status'])
        return JsonResponse({'status': 'failed', 'message': 'Order ID mismatch'}, status=400)

    if not booking.razorpay_order_id or booking.payment_amount != booking.total_fare:
        return JsonResponse({'status': 'failed', 'message': 'Payment order is invalid or expired.'}, status=400)

    try:
        client = _razorpay_client()
        client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature,
        })
        payment = client.payment.fetch(razorpay_payment_id)
        if (payment.get('order_id') != booking.razorpay_order_id or
                payment.get('amount') != _amount_in_paise(booking.payment_amount) or
                payment.get('status') != 'captured'):
            raise ValueError('Payment was not captured for this booking.')

        with transaction.atomic():
            locked_booking = Booking.objects.select_for_update().get(pk=booking.pk)
            if locked_booking.payment_status == 'PAID':
                return JsonResponse({'status': 'already_paid', 'redirect': f'/bookings/payment-success/{booking.booking_id}/'})
            locked_booking.payment_status = 'PAID'
            locked_booking.razorpay_payment_id = razorpay_payment_id
            locked_booking.razorpay_signature = razorpay_signature
            locked_booking.payment_method = payment.get('method', '')
            locked_booking.transaction_date = timezone.now()
            locked_booking.save(update_fields=[
                'payment_status', 'razorpay_payment_id', 'razorpay_signature',
                'payment_method', 'transaction_date', 'updated_at'
            ])
            booking = locked_booking

        # Notify coolie
        if booking.coolie:
            Notification.objects.create(
                recipient=booking.coolie.user,
                title="New Paid Booking Request 🧳",
                message=f"Passenger {request.user.get_full_name() or request.user.username} paid ₹{booking.total_fare} for booking {booking.booking_id}.",
                notification_type='BOOKING',
                link_url="/coolies/dashboard/"
            )

        notify_booking_created(booking)
        return JsonResponse({'status': 'success', 'redirect': f'/bookings/payment-success/{booking.booking_id}/'})

    except Exception:
        booking.payment_status = 'FAILED'
        booking.save(update_fields=['payment_status', 'updated_at'])
        return JsonResponse({'status': 'failed', 'message': 'Payment could not be verified.'}, status=400)


@login_required
def payment_success_view(request, booking_id):
    """Show payment success page — only if payment is verified."""
    booking = get_object_or_404(Booking, booking_id=booking_id, passenger=request.user)
    if booking.payment_status != 'PAID':
        messages.error(request, "Payment not verified. Please complete payment.")
        return redirect('bookings:payment', booking_id=booking_id)
    return render(request, 'bookings/payment_success.html', {'booking': booking})


@login_required
def payment_failed_view(request, booking_id):
    """Show payment failed page."""
    booking = get_object_or_404(Booking, booking_id=booking_id, passenger=request.user)
    if booking.payment_status != 'PAID':
        booking.payment_status = 'FAILED'
        booking.save(update_fields=['payment_status', 'updated_at'])
    return render(request, 'bookings/payment_failed.html', {'booking': booking})


@login_required
def booking_tracking_view(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id)

    if not (booking.passenger == request.user or
            (hasattr(request.user, 'coolie_profile') and booking.coolie == request.user.coolie_profile) or
            request.user.role == 'ADMIN' or request.user.is_superuser):
        messages.error(request, "Unauthorized access to this booking.")
        return redirect('accounts:passenger_dashboard')

    existing_review = getattr(booking, 'review', None)

    # Handle review submission
    if request.method == 'POST' and 'submit_review' in request.POST and booking.status == 'COMPLETED':
        if existing_review:
            messages.info(request, "You have already submitted a review for this booking.")
        else:
            rating = int(request.POST.get('rating', 5))
            punctuality = int(request.POST.get('punctuality_rating', 5))
            behavior = int(request.POST.get('behavior_rating', 5))
            comment = request.POST.get('comment', '').strip()

            Review.objects.create(
                booking=booking,
                passenger=request.user,
                coolie=booking.coolie,
                rating=rating,
                punctuality_rating=punctuality,
                behavior_rating=behavior,
                comment=comment
            )
            messages.success(request, "Thank you! Your rating and review have been submitted.")
            return redirect('bookings:tracking', booking_id=booking.booking_id)

    # Handle cancellation
    if request.method == 'POST' and 'cancel_booking' in request.POST:
        if booking.status in ['REQUESTED', 'ACCEPTED']:
            reason = request.POST.get('cancellation_reason', 'Cancelled by passenger')
            booking.status = 'CANCELLED'
            booking.cancellation_reason = reason
            booking.save()

            if booking.coolie:
                Notification.objects.create(
                    recipient=booking.coolie.user,
                    title="Booking Cancelled",
                    message=f"Booking {booking.booking_id} was cancelled by passenger.",
                    notification_type='BOOKING',
                    link_url="/coolies/dashboard/"
                )
            messages.info(request, "Your booking has been cancelled.")
            return redirect('bookings:tracking', booking_id=booking.booking_id)

    context = {
        'booking': booking,
        'existing_review': existing_review,
    }
    return render(request, 'bookings/booking_tracking.html', context)


@login_required
def booking_history_view(request):
    """
    List of past and active bookings for the logged-in passenger.
    """
    bookings = Booking.objects.filter(passenger=request.user).order_by('-created_at')
    return render(request, 'bookings/booking_history.html', {'bookings': bookings})


# --- REST API ViewSets ---

class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN' or user.is_superuser:
            return Booking.objects.all()
        elif user.role == 'COOLIE' and hasattr(user, 'coolie_profile'):
            return Booking.objects.filter(coolie=user.coolie_profile)
        return Booking.objects.filter(passenger=user)

    def perform_create(self, serializer):
        serializer.save(passenger=self.request.user)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        booking = self.get_object()
        new_status = request.data.get('status')
        if new_status in dict(Booking.STATUS_CHOICES):
            booking.status = new_status
            if new_status == 'ACCEPTED':
                booking.accepted_at = timezone.now()
            elif new_status == 'SERVICE_STARTED':
                booking.started_at = timezone.now()
            elif new_status == 'COMPLETED':
                booking.completed_at = timezone.now()
                if booking.coolie:
                    booking.coolie.total_bookings_count += 1
                    booking.coolie.daily_earnings += booking.total_fare
                    booking.coolie.save()
            booking.save()
            return Response({'status': 'updated', 'booking_status': booking.status})
        return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
