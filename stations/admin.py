from django.contrib import admin
from .models import Station, Platform, Facility


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
	list_display = ('name', 'code', 'city', 'latitude', 'longitude', 'is_active')
	search_fields = ('name', 'code', 'city')
	list_filter = ('is_active', 'state')


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
	list_display = ('station', 'number', 'latitude', 'longitude', 'has_lift', 'has_escalator')
	list_filter = ('station', 'has_lift', 'has_escalator')
	search_fields = ('station__name', 'station__code', 'description')


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
	list_display = ('name', 'station', 'facility_type', 'latitude', 'longitude', 'is_operational')
	list_filter = ('station', 'facility_type', 'is_operational')
	search_fields = ('name', 'station__name', 'station__code', 'location_description')
