import os
from google import genai
from dotenv import load_dotenv
load_dotenv()


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

result = client.models.embed_content(
        model="gemini-embedding-2",
        contents="What is the meaning of life?"
)

print(result.embeddings)