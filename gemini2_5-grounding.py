from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)




interaction = client.interactions.create(
    model="gemini-3.5-flash-lite",
    input="Find good coffee shops near Phnom Penh.",
    tools=[
        {
            "type": "google_maps",
            "latitude": 11.5564,
            "longitude": 104.9282
        }
    ]
)
print(interaction.output_text)