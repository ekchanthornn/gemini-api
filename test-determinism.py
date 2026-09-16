import sys
from dotenv import load_dotenv
from google import genai
import os

load_dotenv()
sys.stdout.reconfigure(encoding="utf-8")

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

PROMPT = "Write a one-sentence creative description of Cambodia in English."
RUNS = 2

print("=" * 60)
print("  interactions.create with temperature=0 and seed=42")
print("  (same config repeated 5x — will answers match?)")
print("=" * 60)

outputs = []
for i in range(1, RUNS + 1):
    interaction = client.interactions.create(
        model="gemma-4-31b-it",
        input=PROMPT,
        # យើងបន្ថែម "seed": 42 នៅទីនេះដើម្បីចាក់សោរការគណនា
        # generation_config={"temperature": 1.9, "top_p": 0.9, "top_k": 400, "seed": 42},
        generation_config={"temperature": 0.0, "top_p": 0.9, "top_k": 10},
    )
    text = interaction.output_text.strip()
    outputs.append(text)
    print(f"\n  Run {i}: {text}")

all_same = len(set(outputs)) == 1
print(f"\n  RESULT: {'ALL SAME (deterministic!)' if all_same else f'DIFFERENT ({len(set(outputs))} unique answers)'}")