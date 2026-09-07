import base64
from dotenv import load_dotenv
from google import genai
import os
load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

interaction = client.interactions.create(
    model="gemini-3.1-flash-image",  # ← Model Image Generation
    input="Generate an image of a futuristic city skyline at sunset",
)
interaction = client.interactions.create(
    model="gemini-2.5-flash-image",  # ← Model Image Generation
    input="បង្កើតរូបភាពកូនសិស្សស្រីជនជាតិខ្មែរកំពុងរៀនគណិតវិទ្យាក្នុងថ្នាក់",
)
# interaction = client.interactions.create(
#     model="gemini-3.1-flash-lite-image",  # ← Model Image Generation
#     input="បង្កើតរូបភាពកូនសិស្សស្រីជនជាតិខ្មែរកំពុងរៀនគណិតវិទ្យាក្នុងថ្នាក់",
# )
# រក្សា Image
with open("generated_image.png", "wb") as f:
    f.write(base64.b64decode(interaction.output_image.data))
print("រូបភាពបានរក្សាទុក!")