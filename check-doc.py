import base64
from dotenv import load_dotenv
from google import genai
import os
load_dotenv()
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)
# Load រូបភាព Local
with open("pp.jpg", "rb") as f:
    image_b64 = base64.b64encode(f.read()).decode("utf-8")
        
interaction = client.interactions.create(
    model="gemini-3.5-flash-lite",
    input=[
        {"type": "text", "text": "តើនេះជាឯកសារអ្វី?"},
        {
            "type": "image",
            "data": image_b64,
            "mime_type": "image/jpeg"
        },
    ]
)
print(interaction.output_text)