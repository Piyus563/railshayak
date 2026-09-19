from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('book/', views.book_coolie_view, name='book_coolie'),
    path('track/<str:booking_id>/', views.booking_tracking_view, name='tracking'),
    path('history/', views.booking_history_view, name='history'),
    # Payment routes
    path('payment/<str:booking_id>/', views.payment_page_view, name='payment'),
    path('payment/<str:booking_id>/create/', views.create_payment_view, name='create_payment'),
    path('payment/<str:booking_id>/verify/', views.verify_payment_view, name='verify_payment'),
    path('payment-success/<str:booking_id>/', views.payment_success_view, name='payment_success'),
    path('payment-failed/<str:booking_id>/', views.payment_failed_view, name='payment_failed'),
]
