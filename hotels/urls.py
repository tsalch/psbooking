from django.urls import path

from . import views

app_name = 'hotels'

urlpatterns = [
    path('hotel-list/', views.HotelListView.as_view(), name='hotel_list'),
    path('hotel-booking/<int:pk>/', views.HotelDetailView.as_view(), name='hotel_booking'),
    path('room-book/<int:pk>/', views.room_book, name='room_book'),
    path('reserv-cancel/<int:pk>/', views.ReservationDeleteView.as_view(), name='reserv_cancel'),
    path('hotel-send-review/', views.HotelSendReview.as_view(), name='hotel_send_review'),
    path('hotel-create/', views.HotelCreateView.as_view(), name='hotel_create'),
    path('hotel-update/<int:pk>/', views.HotelUpdateView.as_view(), name='hotel_update'),

    path('room-create/<int:hotel_pk>/', views.RoomCreateView.as_view(), name='room_create'),
    path('room-update/<int:pk>/', views.RoomUpdateView.as_view(), name='room_update'),
]
