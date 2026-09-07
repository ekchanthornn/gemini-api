
from dotenv import load_dotenv
from google import genai
import os

load_dotenv()
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

stream  = client.interactions.create(
    model="gemini-3.5-flash-lite",
    input="ពន្យល់ AI ក្នុងពាក្យពីរបី",
    stream=True
)

for event in stream:
    print(event)  # print ជា chunk
    


