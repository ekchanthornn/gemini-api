# =====================================================================
# មេរៀន: RAG (Retrieval-Augmented Generation) ជាមួយ Gemini API
# =====================================================================
#
# RAG = Retrieval-Augmented Generation
#
# គំនិតចម្បង:
#   ជំនួសឱ្យការសួរ AI ដោយផ្ទាល់ (ដែល AI មិនដឹងអំពីទិន្នន័យរបស់អ្នក),
#   យើងធ្វើ 3 ជំហានដូចខាងក្រោម:
#
#   [ឯកសាររបស់អ្នក] -> [Retrieve ផ្នែកពាក់ព័ន្ធ] -> [ផ្ញើទៅ Gemini]
#
# =====================================================================

from dotenv import load_dotenv
from google import genai
import os
import math

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# =====================================================================
# ជំហានទី 1: Knowledge Base (ឯកសារ/ទិន្នន័យរបស់អ្នក)
# =====================================================================

documents = [
    {
        "id": "doc_1",
        "title": "ប្រវត្តិក្រុងភ្នំពេញ",
        "content": """
        ភ្នំពេញជារាជធានី និងជាក្រុងធំបំផុតនៃព្រះរាជាណាចក្រកម្ពុជា។
        ក្រុងនេះត្រូវបានបង្កើតឡើងក្នុងឆ្នាំ 1434 ដោយព្រះបាទពញាយ៉ាត។
        ភ្នំពេញមានប្រជាជនប្រមាណ 2 លាននាក់ ហើយស្ថិតនៅចំណុចប្រសព្វ
        នៃទន្លេមេគង្គ និងទន្លេសាប។
        """
    },
    {
        "id": "doc_2",
        "title": "Gemini API គឺជាអ្វី",
        "content": """
        Gemini API គឺជា API របស់ Google សម្រាប់ប្រើប្រាស់ AI Model ឈ្មោះ Gemini។
        Gemini អាចអានអត្ថបទ រូបភាព វីដេអូ និងអូឌីយ៉ូ។
        API Key អាចទទួលបានដោយឥតគិតថ្លៃនៅ Google AI Studio (aistudio.google.com)។
        Model ស្នូលរួមមាន: gemini-2.5-pro, gemini-2.5-flash, gemini-3.6-flash។
        """
    },
    {
        "id": "doc_3",
        "title": "Python Programming Language",
        "content": """
        Python គឺជាភាសា Programming ដែលងាយស្រួលរៀន និងពេញនិយមបំផុតក្នុងពិភពលោក។
        Python ត្រូវបានបង្កើតដោយ Guido van Rossum ក្នុងឆ្នាំ 1991។
        Python ប្រើ Indentation (space/tab) ជំនួសឱ្យ {} brackets។
        Python ត្រូវបានប្រើក្នុង AI/ML, Web Development, Data Science, Automation។
        """
    },
    {
        "id": "doc_4",
        "title": "Machine Learning",
        "content": """
        Machine Learning (ML) គឺជាសាខាមួយនៃ AI ដែល Computer រៀន Pattern ពី Data។
        ML មាន 3 ប្រភេទចំបងៗ: Supervised, Unsupervised, Reinforcement Learning។
        Supervised Learning ប្រើ Data ដែលមាន Label (ឧ. ចាត់ប្រភេទអ៊ីម៉ែល Spam/Not Spam)។
        Deep Learning ប្រើ Neural Network ដែលត្រៀបដូច Brain របស់មនុស្ស។
        """
    }
]

print("=" * 60)
print("Knowledge Base មាន {} ឯកសារ".format(len(documents)))
print("=" * 60)


# =====================================================================
# ជំហានទី 2: Embedding - បំលែង text ទៅជា vector
# =====================================================================
# vector = array of numbers ដែលតំណាងឱ្យ "ន័យ" នៃ text
# texts ដែលមានន័យដូចគ្នា នឹងមាន vectors ជិតគ្នា

def get_embedding(text: str) -> list:
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    )
    return result.embeddings[0].values


# =====================================================================
# ជំហានទី 3: Index Documents
# =====================================================================
# គណនា Embedding សម្រាប់ document ទាំងអស់ រក្សាទុក memory

print("\nIndexing documents...")

indexed_docs = []
for doc in documents:
    text_to_embed = doc["title"] + " " + doc["content"]
    embedding = get_embedding(text_to_embed)
    indexed_docs.append({**doc, "embedding": embedding})
    print("  OK: '{}' -> vector dim: {}".format(doc["title"], len(embedding)))

print("\nEmbedding dimension: {}".format(len(indexed_docs[0]["embedding"])))


# =====================================================================
# ជំហានទី 4: Cosine Similarity Search
# =====================================================================
# Cosine Similarity: វាស់ "ជ្រុង" រវាង vectors 2
# - 1.0  = ដូចគ្នាទាំងស្រុង
# - 0.0  = ចៃដន្យ
# - -1.0 = ផ្ទុយគ្នា

def cosine_similarity(vec_a: list, vec_b: list) -> float:
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    magnitude_a = math.sqrt(sum(a ** 2 for a in vec_a))
    magnitude_b = math.sqrt(sum(b ** 2 for b in vec_b))
    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0
    return dot_product / (magnitude_a * magnitude_b)


def retrieve(query: str, top_k: int = 2) -> list:
    """
    Retrieve ឯកសារ top_k ដែលពាក់ព័ន្ធបំផុតជាមួយ query
    """
    query_embedding = get_embedding(query)

    scored_docs = []
    for doc in indexed_docs:
        score = cosine_similarity(query_embedding, doc["embedding"])
        scored_docs.append({**doc, "score": score})

    scored_docs.sort(key=lambda x: x["score"], reverse=True)
    return scored_docs[:top_k]


# =====================================================================
# ជំហានទី 5: RAG Function - Retrieve + Augment + Generate
# =====================================================================

def rag_answer(question: str) -> str:
    """
    RAG Pipeline:
    1. Retrieve  : ស្វែងរក documents ដែលពាក់ព័ន្ធ
    2. Augment   : បន្ថែម context ទៅក្នុង prompt
    3. Generate  : ឱ្យ Gemini បង្កើតចម្លើយ
    """

    # STEP 1: RETRIEVE
    print("\nSearching for: '{}'".format(question))
    relevant_docs = retrieve(question, top_k=2)

    print("Documents found:")
    for i, doc in enumerate(relevant_docs):
        print("  {}. [score:{:.3f}] {}".format(i+1, doc["score"], doc["title"]))

    # STEP 2: AUGMENT
    context = "\n\n".join([
        "[Doc {}: {}]\n{}".format(i+1, doc["title"], doc["content"].strip())
        for i, doc in enumerate(relevant_docs)
    ])

    augmented_prompt = """អ្នកគឺជាជំនួយការ AI ដែលឆ្លើយតបជាភាសាខ្មែរ។
ចូរប្រើ Context ខាងក្រោមមកជាមូលដ្ឋានក្នុងការឆ្លើយ។
ប្រសិនបើ Context មិនមានព័ត៌មានគ្រប់គ្រាន់ សូមនិយាយថា "ខ្ញុំមិនមានព័ត៌មាននេះ"។

=== CONTEXT ===
{}
=== ចប់ CONTEXT ===

សំណួរ: {}

ចម្លើយ:""".format(context, question)

    # STEP 3: GENERATE
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=augmented_prompt
    )

    return response.text


# =====================================================================
# ជំហានទី 6: សាកល្បង RAG System
# =====================================================================

questions = [
    "ភ្នំពេញត្រូវបានបង្កើតនៅឆ្នាំណា?",
    "Gemini API ប្រើ model អ្វីខ្លះ?",
    "Python ត្រូវបានបង្កើតដោយអ្នកណា?",
    "Machine Learning មានប្រភេទអ្វីខ្លះ?",
]

print("\n" + "=" * 60)
print("RAG Question & Answering System")
print("=" * 60)

for question in questions:
    print("\n" + "-" * 60)
    print("QUESTION: {}".format(question))
    answer = rag_answer(question)
    print("ANSWER:\n{}".format(answer))

print("\n" + "=" * 60)
print("RAG Pipeline Done!")
print("=" * 60)

# =====================================================================
# សង្ខេប RAG Pipeline:
#
#  [User Question]
#       |
#  [Embed Question] <- gemini-embedding-001
#       |
#  [Search Similar Docs] <- Cosine Similarity
#       |
#  [Build Prompt + Context] <- Augment
#       |
#  [Gemini Generate Answer] <- gemini-3.6-flash
#       |
#  [Answer to User]
#
# =====================================================================
