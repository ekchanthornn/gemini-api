import chromadb

# Connect to existing ChromaDB
db = chromadb.PersistentClient(
    path="./chroma_db"
)

# Get collection
collection = db.get_collection(
    name="knowledge"
)

# 1. Count records
print("Total records:", collection.count())

# 2. Get all records
data = collection.get(
    include=[
        "documents",
        "metadatas",
        "embeddings"
    ]
)

# 3. Display records
for i in range(len(data["ids"])):
    print("\n" + "=" * 50)

    print("ID:", data["ids"][i])

    print("Document:")
    print(data["documents"][i])

    print("Metadata:")
    print(data["metadatas"][i])

    print("Embedding:")
    print(data["embeddings"][i])