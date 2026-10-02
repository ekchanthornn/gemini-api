# ingest.py

from dotenv import load_dotenv
from google import genai
import chromadb
import os
import hashlib

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

db = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = db.get_or_create_collection(
    name="knowledge"
)


def get_embedding(text):
    response = client.models.embed_content(
        model="gemini-embedding-2",
        contents=text
    )

    return response.embeddings[0].values


def chunk_text(text, chunk_size=500):
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)

    return chunks


def ingest_document(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()

    chunks = chunk_text(text)

    for index, chunk in enumerate(chunks):
        embedding = get_embedding(chunk)

        chunk_id = hashlib.sha256(
            chunk.encode("utf-8")
        ).hexdigest()

        collection.upsert(
            ids=[chunk_id],
            documents=[chunk],
            embeddings=[embedding],
            metadatas=[{
                "source": file_path,
                "chunk_index": index
            }]
        )

    print(f"Inserted {len(chunks)} chunks")


if __name__ == "__main__":
    ingest_document("documents/khmer_history1.txt")
