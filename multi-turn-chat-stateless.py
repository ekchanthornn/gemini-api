
from dotenv import load_dotenv
from google import genai
import os
load_dotenv()
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)
history = [
    {"type": "user_input", "content": [{"type": "text", "text": "ខ្ញុំមានឆ្កែ ២ ក្បាល។"}]}
]

interaction1 = client.interactions.create(
    model="gemini-3.5-flash-lite",
    store=False,   # ← Stateless mode
    input=history
)
# បន្ថែម response ចូល history
for step in interaction1.steps:
    history.append(step.model_dump())

# Turn 2
history.append({"type": "user_input", "content": [{"type": "text", "text": "ក្នុងផ្ទះ មានជើងប៉ុន្មាន?"}]})

interaction2 = client.interactions.create(
    model="gemini-3.5-flash-lite",
    store=False,
    input=history
)
print(interaction2.steps[-1].content[0].text)


    
    
