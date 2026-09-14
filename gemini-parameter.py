import base64
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
import os

load_dotenv()

# Force UTF-8 output so Khmer/Unicode characters print correctly on Windows
sys.stdout.reconfigure(encoding="utf-8")

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# ៣. កំណត់ Parameters ទាំង ៣ (ឧទាហរណ៍នេះសម្រាប់ការងារទូទៅ)
my_config = {
    "temperature": 0.5,
    "top_p": 0.8,
    "top_k": 40
}

# ៤. បញ្ជូនសំណួរដោយភ្ជាប់ជាមួយការកំណត់
interaction = client.interactions.create(
    model="gemini-3.6-flash",
    input="តើបញ្ញាសិប្បនិមិត្តអាចជួយវិស័យអប់រំនៅកម្ពុជាយ៉ាងដូចម្តេចខ្លះ?",
    generation_config=my_config
)

print(interaction.output_text)