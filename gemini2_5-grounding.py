from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# response = client.models.generate_content(
#     model="models/gemini-3.1-pro-preview",
#     contents="What is the latest price of Bitcoin today?",
#     config=types.GenerateContentConfig(
#         tools=[
#             types.Tool(
#                 google_search=types.GoogleSearch()
#             )
#         ]
#     )
# )

# print(response.text)

# response = client.models.generate_content(
#     model="gemini-3.1-flash-lite",

#     contents="Find good coffee shops near Phnom Penh.",

#     config=types.GenerateContentConfig(
#         tools=[
#             types.Tool(
#                 google_maps=types.GoogleMaps()
#             )
#         ],

#         tool_config=types.ToolConfig(
#             retrieval_config=types.RetrievalConfig(
#                 lat_lng=types.LatLng(
#                     latitude=11.5564,
#                     longitude=104.9282
#                 )
#             )
#         )
#     )
# )

# print(response.text)

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