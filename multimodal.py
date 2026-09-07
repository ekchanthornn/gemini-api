import base64
from dotenv import load_dotenv
from google import genai
import os
load_dotenv()
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)
# Load រូបភាព Local
with open("sample.jpg", "rb") as f:
    image_b64 = base64.b64encode(f.read()).decode("utf-8")
    
# Load Audio Local
with open("sample.mp4", "rb") as f:
    audio_b64 = base64.b64encode(f.read()).decode("utf-8")
    
interaction = client.interactions.create(
    model="gemini-3.5-flash-lite",
    input=[
        {"type": "text", "text": "ប្រៀបធៀបរូបភាព និង Audio ខាងក្រោម"},
        {
            "type": "image",
            "data": image_b64,
            "mime_type": "image/jpeg"
        },
        # {
        #     "type": "audio",
        #     "uri": "https://storage.googleapis.com/generativeai-downloads/data/sample.mp3",
        #     "mime_type": "audio/mp3"
        # }
        {
            "type": "video",
            "data": audio_b64,
            "mime_type": "video/mp4"
        }
    ]
)
print(interaction.output_text)