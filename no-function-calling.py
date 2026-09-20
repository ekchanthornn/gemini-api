from dotenv import load_dotenv
from google import genai
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# សួរ Gemini ដោយផ្ទាល់ — គ្មាន function call, គ្មាន real-time API
interaction = client.interactions.create(
    model="gemini-3.5-flash-lite",
    input="សូមឆ្លើយជាភាសាខ្មែរ។ អាកាសធាតុភ្នំពេញថ្ងៃនេះ?"
)

print("=== គ្មាន Function Call ===")
print(interaction.output_text)
