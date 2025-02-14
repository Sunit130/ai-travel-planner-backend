import json

from pydantic import ValidationError
from django.conf import settings
from planner.services.types import Itinerary
from planner.constants import LLM_ITINERARY_PROMPT
from groq import Groq

groq = Groq(api_key=settings.GORQ_API_KEY)

class LLMPlanner():

    def __init__(self, data):
        self.destination = data.get("destination", "Bangalore")
        self.duration = data.get("duration", "7 days")
        self.travel_type = data.get("travel_type", "Solo / Family")
        self.budget = data.get("budget", "No Range")
        self.interests = data.get("interests", "exploring")

    @staticmethod
    def extract_data_from_content(content):
        start_str, end_str = content.find('{'), content.rfind('}') + 1
        json_str = content[start_str:end_str]
        data = json.loads(json_str)
        return data

    def get_llm_payload(self):
        print(
            self.destination,
            self.duration,
            self.travel_type,
            self.budget,
            self.interests,
        )

        llm_prompt = LLM_ITINERARY_PROMPT \
                        .replace("{destination}", self.destination) \
                        .replace("{duration}", str(self.duration)) \
                        .replace("{travel_type}", self.travel_type) \
                        .replace("{budget}", str(self.budget)) \
                        .replace("{interests}", self.interests) \
                        .replace("{response_format}",  json.dumps(Itinerary.model_json_schema(), indent=2)) \

        return [
            {
                "role": "user",
                "content": 	llm_prompt
            }
        ]


    def get_itinerary(self) -> Itinerary:
        messages = self.get_llm_payload()
        max_retries = 3

        for attempt in range(max_retries):
            chat_completion = groq.chat.completions.create(
                messages=messages,
                model="llama3-70b-8192",
                temperature=0,
                stream=False,
                response_format={"type": "json_object"},
            )
            try:
                itinerary = chat_completion.choices[0].message.content
                print("itinerary : ", itinerary)
                Itinerary.model_validate_json(itinerary)
                return json.loads(itinerary)
            except ValidationError as e:
                print(f"Attempt {attempt + 1} failed with validation error: {e}")
                if attempt < max_retries - 1:
                    continue
                else:
                    raise


