from django.urls import path
from .views import ItineraryDetailView, ItineraryListCreateView, ItineraryListView

urlpatterns = [
    path('create-itinerary/', ItineraryListCreateView.as_view(), name='itinerary-list-create'),
    path('itinerary/<str:destination>/<int:duration>-days/<uuid:itinerary_id>/', ItineraryDetailView.as_view(), name='itinerary-detail'),
    path('itineraries/', ItineraryListView.as_view(), name='itineraries-list'),
]

