from rest_framework import serializers
from .models import Itinerary, Vote

class ItinerarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Itinerary
        fields = '__all__'

class ItineraryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Itinerary
        fields = ['id', 'location_image', 'location', 'headline', 'destination_slug', 'duration', 'created_at', 'interests']


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = '__all__'