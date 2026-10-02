# chat.py

from dotenv import load_dotenv
from google import genai
import chromadb
import os

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

db = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = db.get_collection(
    name="knowledge"
)


def get_embedding(text):
    response = client.models.embed_content(
        model="gemini-embedding-2",
        contents=text
    )

    return response.embeddings[0].values


def search_knowledge(question, top_k=3):
    query_embedding = get_embedding(question)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    return results["documents"][0]


def ask_gemini(question):
    chunks = search_knowledge(question)

    context = "\n\n".join(chunks)

    prompt = f"""
Answer the question using the context below.

Context:
{context}

Question:
{question}

If the answer is not in the context,
say you do not know.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text


if __name__ == "__main__":
    question = input("Ask: ")

    answer = ask_gemini(question)

    print("\nAnswer:")
    print(answer)