import uuid
from django.utils.text import slugify
from django.db import models
from django.contrib.auth.models import User

class Itinerary(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    headline = models.TextField(default="")
    subheadline = models.TextField(default="")
    quote = models.TextField(default="")
    location = models.CharField(max_length=100, default="")
    location_image = models.TextField(default="")
    destination = models.CharField(max_length=100)
    destination_slug = models.SlugField(max_length=100, blank=True)
    duration = models.IntegerField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    interests = models.TextField()
    overview_introduction = models.TextField()
    overview_time_to_visit = models.TextField()
    top_attractions = models.TextField()
    interest_attractions = models.TextField()
    itinerary_plan = models.JSONField(default=list)
    images_by_day = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.destination_slug = slugify(self.destination)  # Convert "New York" → "new-york"
        super().save(*args, **kwargs)

class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE)
    is_upvote = models.BooleanField(default=True)