from django.urls import path
from . import views

app_name = 'stations'

urlpatterns = [
    path('', views.station_list_view, name='station_list'),
    path('map/', views.station_map_view, name='station_map_default'),
    path('map/<str:code>/', views.station_map_view, name='station_map'),
    path('<str:code>/', views.station_detail_view, name='station_detail'),
]
