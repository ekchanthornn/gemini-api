# from dotenv import load_dotenv
# from google import genai
# import os

# load_dotenv()

# client = genai.Client(
#     api_key=os.getenv("GEMINI_API_KEY")
# )

# interaction = client.interactions.get(id=created.id)
# print(interaction.status)

from dotenv import load_dotenv
from google import genai
import os

load_dotenv()
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

interaction = client.interactions.create(
    model="gemini-3.5-flash-lite",
    input="ពន្យល់ AI ក្នុងពាក្យពីរបី"
)

print(interaction.output_text)
# print(interaction)

