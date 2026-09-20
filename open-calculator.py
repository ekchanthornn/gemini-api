from dotenv import load_dotenv
from google import genai
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

tools = [
    {
        "type": "computer_use",
        "environment": "desktop"   # browser | desktop | mobile
    }
]

interaction = client.interactions.create(
    model="gemini-3.8-flash",     # model ដែល support computer_use
    input="សូមបើកកម្មវិធី Calculator",
    tools=tools
)

print(interaction)