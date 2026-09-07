
from dotenv import load_dotenv
from google import genai
import os
load_dotenv()
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)
interaction1 = client.interactions.create(
    model="gemini-3.5-flash-lite",
    input="ខ្ញុំមានឆ្កែ ២ ក្បាល។"
)
print("Response 1:", interaction1.output_text)
# Turn 2 — ភ្ជាប់ ID ពី Turn ដំបូង
interaction2 = client.interactions.create(
    model="gemini-3.5-flash-lite",
    input="ក្នុងផ្ទះខ្ញុំ មានជើងសត្វប៉ុន្មាន?",
    previous_interaction_id=interaction1.id,  
)
print("Response 2:", interaction2.output_text)
# Output: "ក្នុងផ្ទះអ្នក មានជើង ៨ (ឆ្កែ ២ × ជើង ៤)"