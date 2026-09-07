from dotenv import load_dotenv
from google import genai
import os
load_dotenv()   # អាន .env file
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
interaction = client.interactions.create(
    model="gemini-3.5-flash-lite",
    input="Explain how AI works in a few words"
)
print(interaction.output_text)
