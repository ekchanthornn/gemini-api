from dotenv import load_dotenv
from google import genai
import os

load_dotenv()
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# សួរ Gemini ដោយផ្ទាល់ — គ្មាន function call, គ្មាន real-time API
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="អាកាសធាតុភ្នំពេញថ្ងៃនេះ?"
)

print("=== គ្មាន Function Call ===")
print(response.text)
