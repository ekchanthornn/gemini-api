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
    input="សូមពន្យល់សង្ខេបអំពី AI"
)

print(interaction.output_text)
# print(interaction)

