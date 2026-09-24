from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import Facility, Platform, Station

class StationMapTests(TestCase):
	def setUp(self):
		self.station = Station.objects.create(
			name='Test Station', code='TST', city='Test City', state='Test State',
			latitude=Decimal('26.685300'), longitude=Decimal('88.441800'),
		)
		self.platform = Platform.objects.create(station=self.station, number=1)
		self.facility = Facility.objects.create(
			station=self.station, facility_type='COOLIE_PICKUP', name='Pickup Point',
			location_description='Main entrance', latitude=None, longitude=None,
		)

	def test_map_api_preserves_missing_coordinates(self):
		response = self.client.get(reverse('api_stations-map-data', args=[self.station.code]))

		self.assertEqual(response.status_code, 200)
		payload = response.json()
		self.assertEqual(payload['station']['code'], 'TST')
		self.assertIsNone(payload['platforms'][0]['latitude'])
		self.assertIsNone(payload['facilities'][0]['latitude'])
		self.assertEqual(payload['facilities'][0]['facility_type'], 'COOLIE_PICKUP')

	def test_coordinate_pair_must_be_complete(self):
		self.platform.longitude = Decimal('88.441800')

		with self.assertRaises(ValidationError):
			self.platform.full_clean()

	def test_invalid_coordinate_range_is_rejected(self):
		self.facility.latitude = Decimal('91')
		self.facility.longitude = Decimal('88.441800')

		with self.assertRaises(ValidationError):
			self.facility.full_clean()
