from dotenv import load_dotenv
from google import genai
import os
load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# Managed Agent — Google គ្រប់គ្រង Loop ស្វ័យប្រវត្តិ
agent = client.agents.create(
    model="gemini-3.8-flash",
    tools=[
        {"type": "google_search"},
        {"type": "code_execution"}
    ],
    system_instruction="អ្នកជា Research Assistant ជំនួយការ"
)
result = agent.run(
    "ស្វែងរកព័ត៌មានអំពី Gemini API ហើយ Summary ជា Bullet Points"
)
print(result.output_text)