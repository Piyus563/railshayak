from decimal import Decimal
<<<<<<< HEAD
from django.test import TestCase, Client
=======
from unittest.mock import Mock, patch
from django.test import TestCase, Client
from django.test import override_settings
>>>>>>> dd5170b (Initial RailSaathi deployment-ready commit)
from django.urls import reverse
from django.utils import timezone

from accounts.models import User, PassengerProfile, CoolieProfile
from stations.models import Station, Platform, Facility
from bookings.models import Booking
from assistance.models import AssistanceRequest
from lost_found.models import LostFoundReport
from complaints.models import Complaint
from reviews.models import Review


class RailSaathiCoreTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create Station & Platform
        self.station = Station.objects.create(
            name="New Jalpaiguri Junction",
            code="NJP",
            city="Siliguri",
            state="West Bengal",
            number_of_platforms=5,
            latitude=Decimal('26.6853'),
            longitude=Decimal('88.4418')
        )
        self.platform1 = Platform.objects.create(
            station=self.station,
            number=1,
            description="Main Line",
            has_lift=True,
            has_escalator=True
        )

        # Create Admin
        self.admin_user = User.objects.create_superuser(
            username="admin_test",
            email="admin@test.com",
            password="adminpassword",
            role="ADMIN"
        )

        # Create Passenger
        self.passenger_user = User.objects.create_user(
            username="passenger_test",
            email="passenger@test.com",
            password="passpassword",
            first_name="Priya",
            last_name="Singh",
            role="PASSENGER",
            phone="+91 9876543210"
        )
        self.passenger_profile = PassengerProfile.objects.create(user=self.passenger_user)

        # Create Coolie
        self.coolie_user = User.objects.create_user(
            username="coolie_test",
            email="coolie@test.com",
            password="cooliepassword",
            first_name="Ramesh",
            last_name="Kumar",
            role="COOLIE",
            phone="+91 9871110001"
        )
        self.coolie_profile = CoolieProfile.objects.create(
            user=self.coolie_user,
            badge_number="NJP-C-104",
            station=self.station,
            experience_years=5,
            is_verified=True,
            is_online=True
        )

    def test_01_user_roles_and_authentication(self):
        """Test authentication and role separation"""
        self.assertTrue(self.passenger_user.is_passenger())
        self.assertTrue(self.coolie_user.is_coolie())
        self.assertTrue(self.admin_user.is_station_admin())

        # Test login
        logged_in = self.client.login(username="passenger_test", password="passpassword")
        self.assertTrue(logged_in)
        response = self.client.get(reverse('accounts:passenger_dashboard'))
        self.assertEqual(response.status_code, 200)

<<<<<<< HEAD
=======
    @override_settings(TWILIO_WHATSAPP_ENABLED=False, TWILIO_ACCOUNT_SID='AC123', TWILIO_AUTH_TOKEN='token123')
    @patch('bookings.whatsapp.Client')
    def test_01b_whatsapp_skips_when_disabled(self, mock_client_class):
        """WhatsApp sends must be skipped when Twilio is disabled or not production-ready."""
        message_client = Mock()
        mock_client_class.return_value = message_client

        result = self.client.post(reverse('bookings:book_coolie'), {
            'station_id': self.station.id,
            'platform_id': self.platform1.id,
            'coolie_id': self.coolie_profile.id,
            'journey_type': 'ARRIVAL',
            'train_number': '12042 Shatabdi',
            'coach_number': 'C2',
            'luggage_type': 'TROLLEY',
            'number_of_bags': 1,
            'approx_weight_kg': 15,
            'meeting_point': 'Platform 1 Coach C2 Door',
        })

        self.assertEqual(result.status_code, 302)
        message_client.messages.create.assert_not_called()

>>>>>>> dd5170b (Initial RailSaathi deployment-ready commit)
    def test_02_coolie_availability_toggle(self):
        """Test coolie going online and offline"""
        self.client.login(username="coolie_test", password="cooliepassword")
        self.assertTrue(self.coolie_profile.is_online)

        # Post toggle
        response = self.client.post(reverse('coolies:dashboard'), {'toggle_status': '1'})
        self.assertEqual(response.status_code, 302)
        self.coolie_profile.refresh_from_db()
        self.assertFalse(self.coolie_profile.is_online)

    def test_03_booking_creation_and_fare_calculation(self):
        """Test booking creation with dynamic fare calculation (Base 100 + 50/extra bag)"""
        self.client.login(username="passenger_test", password="passpassword")

        # 3 bags => 100 + 2*50 = 200
        response = self.client.post(reverse('bookings:book_coolie'), {
            'station_id': self.station.id,
            'platform_id': self.platform1.id,
            'coolie_id': self.coolie_profile.id,
            'journey_type': 'ARRIVAL',
            'train_number': '12042 Shatabdi',
            'coach_number': 'C2',
            'luggage_type': 'TROLLEY',
            'number_of_bags': 3,
            'approx_weight_kg': 30,
            'meeting_point': 'Platform 1 Coach C2 Door',
        })
        self.assertEqual(response.status_code, 302)

        booking = Booking.objects.filter(passenger=self.passenger_user).first()
        self.assertIsNotNone(booking)
        self.assertEqual(booking.status, 'REQUESTED')
        self.assertEqual(booking.total_fare, Decimal('200.00'))

<<<<<<< HEAD
=======
    @override_settings(RAZORPAY_KEY_ID='rzp_test_key', RAZORPAY_KEY_SECRET='test_secret')
    @patch('bookings.views._razorpay_client')
    def test_04_payment_verification_confirms_once(self, client_factory):
        booking = Booking.objects.create(
            passenger=self.passenger_user,
            coolie=self.coolie_profile,
            station=self.station,
            platform=self.platform1,
            number_of_bags=2,
            total_fare=Decimal('150.00'),
            payment_status='PENDING',
        )
        gateway = Mock()
        gateway.order.create.return_value = {'id': 'order_test_123'}
        gateway.payment.fetch.return_value = {
            'order_id': 'order_test_123', 'amount': 15000,
            'status': 'captured', 'method': 'upi',
        }
        client_factory.return_value = gateway
        self.client.login(username='passenger_test', password='passpassword')

        create_response = self.client.post(reverse('bookings:create_payment', args=[booking.booking_id]))
        self.assertEqual(create_response.status_code, 200)
        booking.refresh_from_db()
        self.assertEqual(booking.razorpay_order_id, 'order_test_123')
        self.assertEqual(booking.payment_amount, Decimal('150.00'))

        verify_response = self.client.post(reverse('bookings:verify_payment', args=[booking.booking_id]), {
            'razorpay_order_id': 'order_test_123',
            'razorpay_payment_id': 'pay_test_123',
            'razorpay_signature': 'valid_signature',
        })
        self.assertEqual(verify_response.status_code, 200)
        booking.refresh_from_db()
        self.assertEqual(booking.payment_status, 'PAID')
        self.assertEqual(booking.payment_method, 'upi')

        duplicate_response = self.client.post(reverse('bookings:verify_payment', args=[booking.booking_id]), {
            'razorpay_order_id': 'order_test_123',
            'razorpay_payment_id': 'pay_test_123',
            'razorpay_signature': 'valid_signature',
        })
        self.assertEqual(duplicate_response.json()['status'], 'already_paid')

    @override_settings(RAZORPAY_KEY_ID='rzp_test_key', RAZORPAY_KEY_SECRET='test_secret')
    @patch('bookings.views._razorpay_client')
    def test_05_invalid_payment_signature_does_not_confirm(self, client_factory):
        booking = Booking.objects.create(
            passenger=self.passenger_user,
            coolie=self.coolie_profile,
            station=self.station,
            platform=self.platform1,
            number_of_bags=1,
            total_fare=Decimal('100.00'),
            payment_status='PENDING',
            razorpay_order_id='order_test_456',
            payment_amount=Decimal('100.00'),
        )
        gateway = Mock()
        gateway.utility.verify_payment_signature.side_effect = ValueError('invalid signature')
        client_factory.return_value = gateway
        self.client.login(username='passenger_test', password='passpassword')

        response = self.client.post(reverse('bookings:verify_payment', args=[booking.booking_id]), {
            'razorpay_order_id': 'order_test_456',
            'razorpay_payment_id': 'pay_test_456',
            'razorpay_signature': 'invalid_signature',
        })
        self.assertEqual(response.status_code, 400)
        booking.refresh_from_db()
        self.assertEqual(booking.payment_status, 'FAILED')
        self.assertNotEqual(booking.status, 'COMPLETED')

>>>>>>> dd5170b (Initial RailSaathi deployment-ready commit)
    def test_04_coolie_booking_workflow_state_transitions(self):
        """Test full state machine: REQUESTED -> ACCEPTED -> SERVICE_STARTED -> COMPLETED"""
        booking = Booking.objects.create(
            passenger=self.passenger_user,
            coolie=self.coolie_profile,
            station=self.station,
            platform=self.platform1,
            number_of_bags=2,
            total_fare=Decimal('150.00'),
            status='REQUESTED'
        )

        self.client.login(username="coolie_test", password="cooliepassword")

        # Accept
        resp1 = self.client.get(reverse('coolies:update_booking_status', args=[booking.booking_id, 'accept']))
        self.assertEqual(resp1.status_code, 302)
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'ACCEPTED')

        # Start Service
        resp2 = self.client.get(reverse('coolies:update_booking_status', args=[booking.booking_id, 'start']))
        self.assertEqual(resp2.status_code, 302)
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'SERVICE_STARTED')

        # Complete Service
        resp3 = self.client.get(reverse('coolies:update_booking_status', args=[booking.booking_id, 'complete']))
        self.assertEqual(resp3.status_code, 302)
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'COMPLETED')

    def test_05_rating_and_review_recalculation(self):
        """Test passenger leaving star rating & coolie aggregate rating update"""
        booking = Booking.objects.create(
            passenger=self.passenger_user,
            coolie=self.coolie_profile,
            station=self.station,
            platform=self.platform1,
            status='COMPLETED'
        )

        self.client.login(username="passenger_test", password="passpassword")
        response = self.client.post(reverse('bookings:tracking', args=[booking.booking_id]), {
            'submit_review': '1',
            'rating': 5,
            'punctuality_rating': 5,
            'behavior_rating': 5,
            'comment': 'Exceptional service and timely help!'
        })
        self.assertEqual(response.status_code, 302)

        review = Review.objects.filter(booking=booking).first()
        self.assertIsNotNone(review)
        self.assertEqual(review.rating, 5)

        self.coolie_profile.refresh_from_db()
        self.assertEqual(float(self.coolie_profile.rating), 5.0)

    def test_06_assistance_request(self):
        """Test passenger requesting assistance"""
        response = self.client.post(reverse('assistance:request'), {
            'assistance_type': 'WHEELCHAIR',
            'passenger_name': 'Mrs. Usha Singh',
            'passenger_phone': '+91 9876543210',
            'station_id': self.station.id,
            'platform_id': self.platform1.id,
            'description': 'Need wheelchair at coach door',
        })
        self.assertEqual(response.status_code, 302)
        req = AssistanceRequest.objects.filter(passenger_name='Mrs. Usha Singh').first()
        self.assertIsNotNone(req)
        self.assertTrue(req.request_id.startswith('RS-AST-'))

    def test_07_lost_and_found_submission(self):
        """Test lost & found reporting"""
        response = self.client.post(reverse('lost_found:index'), {
            'report_type': 'LOST',
            'item_name': 'Black HP Laptop Bag',
            'category': 'ELECTRONICS',
            'station_id': self.station.id,
            'platform_id': self.platform1.id,
            'description': 'Left inside waiting room',
            'contact_name': 'Priya Singh',
            'contact_phone': '+91 9876543210',
        })
        self.assertEqual(response.status_code, 302)
        lf = LostFoundReport.objects.filter(item_name='Black HP Laptop Bag').first()
        self.assertIsNotNone(lf)
        self.assertTrue(lf.report_id.startswith('RS-LF-'))

    def test_08_complaint_registration(self):
        """Test complaint submission"""
        response = self.client.post(reverse('complaints:submit'), {
            'category': 'CLEANLINESS',
            'station_id': self.station.id,
            'platform_id': self.platform1.id,
            'priority': 'MEDIUM',
            'description': 'Overflowing dustbin on platform',
            'contact_name': 'Priya Singh',
            'contact_phone': '+91 9876543210',
        })
        self.assertEqual(response.status_code, 302)
        cmp = Complaint.objects.filter(contact_name='Priya Singh').first()
        self.assertIsNotNone(cmp)
        self.assertTrue(cmp.ticket_id.startswith('RS-CMP-'))

    def test_09_drf_api_endpoints(self):
        """Test REST API endpoints"""
        # Test public stations API
        resp = self.client.get('/api/v1/stations/')
        self.assertEqual(resp.status_code, 200)

        # Test public coolies API
        resp_coolies = self.client.get('/api/v1/coolies/')
        self.assertEqual(resp_coolies.status_code, 200)

        # Test analytics chart API
        resp_charts = self.client.get('/portal/api/charts-data/')
        self.assertEqual(resp_charts.status_code, 200)
        self.assertIn('daily_bookings', resp_charts.json())

<<<<<<< HEAD
        for endpoint in ('assistance', 'lost-found', 'complaints'):
            response = self.client.post(f'/api/v1/{endpoint}/', {})
            self.assertEqual(response.status_code, 403)

    def test_10_invalid_booking_input_is_rejected(self):
        """Test invalid numeric booking input does not create a server error."""
        self.client.login(username="passenger_test", password="passpassword")
        response = self.client.post(reverse('bookings:book_coolie'), {
            'station_id': self.station.id,
            'number_of_bags': 'not-a-number',
            'approx_weight_kg': 20,
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Booking.objects.filter(passenger=self.passenger_user).count(), 0)

    def test_11_station_map_page_and_data(self):
        """Test the station map page and its live data endpoint."""
        page = self.client.get(reverse('stations:station_map_default'))
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, '/api/v1/stations/NJP/map_data/')
        self.assertContains(page, 'facilities-data')

        map_data = self.client.get('/api/v1/stations/NJP/map_data/')
        self.assertEqual(map_data.status_code, 200)
        self.assertEqual(len(map_data.json()['platforms']), 1)
=======
    def test_10_ai_assistant_and_recommendations(self):
        self.client.login(username="passenger_test", password="passpassword")

        chat_response = self.client.post(reverse('accounts:assistant_chat'), {'message': 'What is the coolie fare?'})
        self.assertEqual(chat_response.status_code, 200)
        self.assertIn('Rs. 100', chat_response.json()['reply'])

        recommendation_response = self.client.get(reverse('accounts:coolie_recommendations'), {
            'station': 'NJP', 'bags': 4, 'assistance': 'true'
        })
        self.assertEqual(recommendation_response.status_code, 200)
        recommendations = recommendation_response.json()['recommendations']
        self.assertEqual(recommendations[0]['badge_number'], 'NJP-C-104')
        self.assertIn('experienced', recommendations[0]['reason'])

    def test_11_ai_endpoints_require_authentication(self):
        chat_response = self.client.post(reverse('accounts:assistant_chat'), {'message': 'map'})
        recommendation_response = self.client.get(reverse('accounts:coolie_recommendations'))
        self.assertEqual(chat_response.status_code, 302)
        self.assertEqual(recommendation_response.status_code, 302)
>>>>>>> dd5170b (Initial RailSaathi deployment-ready commit)
