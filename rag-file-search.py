from dotenv import load_dotenv
from google import genai
import os
import time

# 1. Load Environment Variables
load_dotenv()

# 2. Create Gemini Client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# 3. Create File Search Store
store = client.file_search_stores.create(
    config={
        "display_name": "thnak-academy-knowledge",
        "embedding_model": "models/gemini-embedding-2"
    }
)

print("Store Created:", store.name)

# 4. Upload and Index Document
operation = client.file_search_stores.upload_to_file_search_store(
    file="documents/khmer_history.txt",
    file_search_store_name=store.name,
    config={
        "display_name": "khmer history"
    }
)

# 5. Wait Until Indexing Is Complete
while not operation.done:
    time.sleep(5)
    operation = client.operations.get(operation)

print("Document Indexed Successfully!")

# 6. Ask Question Using RAG
interaction = client.interactions.create(
    model="gemini-3.5-flash-lite",
    input="""
     ចូរឆ្លើយសំណួរដោយប្រើព័ត៌មានពី Knowledge Base ដែលបានផ្តល់។.

    សំណួរ៖
    តើក្រុមមនុស្សដែលបានរស់នៅទីនេះចាប់តាំងពី​សហវត្សទីប៉ុន្មាន?
    """,
    tools=[
        {
            "type": "file_search",
            "file_search_store_names": [
                store.name
            ]
        }
    ]
)

# 7. Print Model Response
for step in interaction.steps:
    if step.type == "model_output":
        for content in step.content:
            if content.type == "text":
                print(content.text)