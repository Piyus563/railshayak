from django.shortcuts import render, get_object_or_404
<<<<<<< HEAD
from django.http import Http404
=======
from django.http import JsonResponse
>>>>>>> dd5170b (Initial RailSaathi deployment-ready commit)
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Station, Platform, Facility
from .serializers import StationSerializer, PlatformSerializer, FacilitySerializer


# --- HTML Views ---

def station_list_view(request):
    """
    List of active stations with search and facility badges.
    """
    query = request.GET.get('q', '').strip()
    stations = Station.objects.filter(is_active=True)
    if query:
        stations = stations.filter(name__icontains=query) | stations.filter(code__icontains=query) | stations.filter(city__icontains=query)

    return render(request, 'stations/station_list.html', {
        'stations': stations,
        'query': query
    })


def station_detail_view(request, code):
    """
    Comprehensive station profile page with platforms, facilities, and live map container.
    """
    station = get_object_or_404(Station, code__iexact=code)
    platforms = station.platforms.all()
    facilities = station.facilities.all()

    # Categorize facilities
    categories = {}
    for f in facilities:
        cat = f.get_facility_type_display()
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(f)

    return render(request, 'stations/station_detail.html', {
        'station': station,
        'platforms': platforms,
        'facilities': facilities,
        'categories': categories,
    })


<<<<<<< HEAD
def station_map_view(request, code=None):
    """
    Interactive station map powered by Leaflet.js and OpenStreetMap.
    """
    if code:
        station = get_object_or_404(Station, code__iexact=code, is_active=True)
    else:
        station = Station.objects.filter(code__iexact='NJP', is_active=True).first()
        station = station or Station.objects.filter(is_active=True).first()
        if station is None:
            raise Http404('No active stations are available.')
=======
def station_map_view(request, code='NJP'):
    """
    Interactive station map powered by Leaflet.js and OpenStreetMap.
    """
    station = get_object_or_404(Station, code__iexact=code)
>>>>>>> dd5170b (Initial RailSaathi deployment-ready commit)
    all_stations = Station.objects.filter(is_active=True)
    facilities = station.facilities.all()
    platforms = station.platforms.all()

    facilities_data = [
        {
            'id': f.id,
            'name': f.name,
            'facility_type': f.facility_type,
            'facility_type_display': f.get_facility_type_display(),
            'location_description': f.location_description,
            'latitude': float(f.latitude) if f.latitude else float(station.latitude),
            'longitude': float(f.longitude) if f.longitude else float(station.longitude),
            'contact_number': f.contact_number or '',
<<<<<<< HEAD
            'is_operational': f.is_operational,
=======
>>>>>>> dd5170b (Initial RailSaathi deployment-ready commit)
        }
        for f in facilities
    ]

    platforms_data = [
        {
            'number': p.number,
            'description': p.description,
            'latitude': float(p.latitude) if p.latitude else float(station.latitude),
            'longitude': float(p.longitude) if p.longitude else float(station.longitude),
        }
        for p in platforms
    ]

    return render(request, 'stations/station_map.html', {
        'station': station,
        'all_stations': all_stations,
<<<<<<< HEAD
        'station_data': {
            'latitude': float(station.latitude),
            'longitude': float(station.longitude),
            'name': station.name,
        },
=======
>>>>>>> dd5170b (Initial RailSaathi deployment-ready commit)
        'facilities': facilities,
        'platforms': platforms,
        'facilities_data': facilities_data,
        'platforms_data': platforms_data,
    })


# --- REST API ViewSets ---

class StationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Station.objects.filter(is_active=True)
    serializer_class = StationSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'code'

    @action(detail=True, methods=['get'])
    def map_data(self, request, code=None):
        station = self.get_object()
<<<<<<< HEAD
        facilities = FacilitySerializer(station.facilities.all(), many=True).data
=======
        facilities = FacilitySerializer(station.facilities.filter(is_operational=True), many=True).data
>>>>>>> dd5170b (Initial RailSaathi deployment-ready commit)
        platforms = PlatformSerializer(station.platforms.all(), many=True).data
        return Response({
            'station': {
                'id': station.id,
                'name': station.name,
                'code': station.code,
                'latitude': float(station.latitude),
                'longitude': float(station.longitude),
            },
            'platforms': platforms,
            'facilities': facilities
        })


class PlatformViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Platform.objects.all()
    serializer_class = PlatformSerializer
    permission_classes = [permissions.AllowAny]


class FacilityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Facility.objects.all()
    serializer_class = FacilitySerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        station_code = self.request.query_params.get('station')
        f_type = self.request.query_params.get('type')
        if station_code:
            qs = qs.filter(station__code__iexact=station_code)
        if f_type:
            qs = qs.filter(facility_type=f_type)
        return qs
