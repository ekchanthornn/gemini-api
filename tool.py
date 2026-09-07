from dotenv import load_dotenv
from google import genai
import os

load_dotenv()
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# interaction = client.interactions.create(
#     model="gemini-3.1-flash-lite",
#     input="Euro 2024 ចំណាត់ថ្នាក់ចុងក្រោយ?",
#     tools=[{"type": "google_search"}]   # ← Enable Search
# )
interaction = client.interactions.create(
    model="gemma-4-31b-it",
    input="Euro 2024 ចំណាត់ថ្នាក់ចុងក្រោយ?",
    tools=[{"type": "google_search"}]   # ← Enable Search
)

print(interaction.output_text)
# Print Citations
for step in interaction.steps:
    if step.type == "model_output":
        for block in step.content:
            if block.type == "text" and block.annotations:
                for ann in block.annotations:
                    if ann.type == "url_citation":
                        print(f"  Source: [{ann.title}]({ann.url})")