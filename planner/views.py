import asyncio
import aiohttp
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User


from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from ai_travel_planner import settings
from planner.serializers import ItineraryListSerializer, ItinerarySerializer
from planner.models import Itinerary, Vote
from planner.services.llm_planner import LLMPlanner


# Create your views here.
class ItineraryListCreateView(APIView):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def populate_itinerary_table(requested_data, itinerary_data, images):
        itinerary = Itinerary.objects.create(
            headline = itinerary_data["headline"],
            subheadline = itinerary_data["subheadline"],
            quote = itinerary_data["quote"],
            location = itinerary_data["location"],
            location_image = images["location_image"],
            destination = requested_data["destination"],
            duration = requested_data["duration"],
            budget = requested_data["budget"],
            interests = requested_data["interests"],
            overview_introduction = itinerary_data["overview"]["introduction"],
            overview_time_to_visit = itinerary_data["overview"]["time_to_visit"],
            top_attractions = itinerary_data["top_attractions"],
            interest_attractions = itinerary_data["interest_attractions"],
            itinerary_plan = itinerary_data["itinerary"],
            images_by_day = images["images_by_day"],
        )

        user = User.objects.get(username="sunit")

        Vote.objects.create(user=user, itinerary=itinerary, is_upvote=True)

        return ItinerarySerializer(itinerary)


    @staticmethod
    async def get_image_for_place(session: aiohttp.ClientSession, place_name: str) -> str:
        """
        Given a place name, first search for the place using Google Places API to get a photo reference,
        then request the photo URL.
        """
        API_KEY = settings.GOOGLE_PLACES_API_KEY
        # Build the URL to search for the place.
        search_url = (
            "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
            f"?input={place_name}"
            "&inputtype=textquery"
            "&fields=photos,place_id"
            f"&key={API_KEY}"
        )

        # Make the asynchronous GET request for the place search.
        async with session.get(search_url) as response:
            data = await response.json()

        if data.get("candidates"):
            candidate = data["candidates"][0]
            if candidate.get("photos"):
                photo_reference = candidate["photos"][0]["photo_reference"]
                # Build the URL to get the photo using the reference.
                image_url = (
                    "https://maps.googleapis.com/maps/api/place/photo"
                    "?maxwidth=800"
                    f"&photoreference={photo_reference}"
                    f"&key={API_KEY}"
                )
                # Make an asynchronous HEAD request to follow the redirect to the actual image URL.
                async with session.head(image_url, allow_redirects=True) as photo_response:
                    if photo_response.status == 200:
                        return str(photo_response.url)
        return ""


    async def get_itinerary_images(self, itinerary_data: dict) -> dict:
        """
        For a given itinerary, concurrently fetch the location image and the images for all places in the itinerary.
        """
        async with aiohttp.ClientSession() as session:
            # Create a task to get the main location image.
            location_image_task = asyncio.create_task(self.get_image_for_place(session, itinerary_data['location']))

            # Dictionary to hold tasks for each day and each place.
            day_tasks = {}
            for day in itinerary_data["itinerary"]:
                day_number = str(day["day"])
                day_tasks[day_number] = {}
                for place in day.get("places", []):
                    # For better results, append the main location to the place.
                    destination = f"{place}, {itinerary_data['location']}"
                    day_tasks[day_number][place] = asyncio.create_task(self.get_image_for_place(session, destination))

            # Await the location image task.
            location_image = await location_image_task

            # Collect results for each day concurrently.
            images_by_day = {}
            for day_number, tasks in day_tasks.items():
                day_images = {}
                # Await all tasks for the current day.
                for place, task in tasks.items():
                    image_url = await task
                    if image_url:
                        day_images[place] = image_url
                images_by_day[day_number] = day_images

            # Debug prints (or log as needed).
            print("location_image:", location_image)
            print("images_by_day:", images_by_day)

            return {
                "location_image": location_image,
                "images_by_day": images_by_day
            }
        

    def post(self, request):
        # add serilizer 

        print("request.data : ", request.data)

        user_requirements = {
            "destination": request.data.get("destination", "Bangalore"),
            "duration": request.data.get("duration", 7),
            "travel_type": request.data.get("travel_type", "Solo / Family"),
            "budget": request.data.get("budget", 10000),
            "interests": str(request.data.get("interests", "exploring")),
        }

        llm_planner = LLMPlanner(user_requirements)
        

        itinerary_data = llm_planner.get_itinerary()
        print("itinerary_data : ", itinerary_data)
        images = asyncio.run(self.get_itinerary_images(itinerary_data))
        serialize_itinerary = self.populate_itinerary_table(user_requirements, itinerary_data, images)
        return Response(serialize_itinerary.data)

    def get(self, request):
        """
        Get a list of all itineraries.
        """
        itineraries = Itinerary.objects.all()
        serializer = ItinerarySerializer(itineraries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ItineraryDetailView(APIView):
    """
    API View to retrieve, update, or delete a specific itinerary.
    """
    def get(self, request, destination, duration, itinerary_id):
        """
        Retrieve a specific itinerary.
        """
        print(duration, destination, itinerary_id)
        itinerary = get_object_or_404(Itinerary, id=itinerary_id, destination_slug=destination, duration=duration)
        serializer = ItinerarySerializer(itinerary)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class ItineraryListView(ListAPIView):
    serializer_class = ItineraryListSerializer

    def get_queryset(self):
        """
        Get the latest itineraries based on the 'limit' query parameter.
        If no limit is provided, return all itineraries.
        """
        limit = self.request.query_params.get('limit', None)
        queryset = Itinerary.objects.order_by('-created_at')

        if limit is not None:
            try:
                limit = int(limit)
                if limit > 0:
                    return queryset[:limit]
            except ValueError:
                pass
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)