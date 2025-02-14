from typing import List
from pydantic import BaseModel

class Overview(BaseModel):
    introduction: str
    time_to_visit: str

class DailyActivity(BaseModel):
    day: int
    title: str
    morning: str
    afternoon: str
    evening: str
    places: List[str]

class Itinerary(BaseModel):
    headline: str
    subheadline: str
    quote: str
    location: str
    destination: str
    duration: int
    overview: Overview
    top_attractions: List[str]
    interest_attractions: List[str]
    itinerary: List[DailyActivity]

