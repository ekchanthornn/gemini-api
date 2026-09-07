from dotenv import load_dotenv
from google import genai
import os

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

text = input("Enter English text: ")

interaction = client.interactions.create(
    model="gemini-3.5-flash-lite",
    input=f"""
Translate the following English text into Khmer.

Rules:
- Translate accurately and naturally.
- Preserve the original meaning.
- Return only the Khmer translation.
- Do not add explanations.

English:
{text}
""",
    generation_config={
        "temperature": 1.0,
        
    }
)

print("\nKhmer:")
print(interaction.output_text)
print(interaction)