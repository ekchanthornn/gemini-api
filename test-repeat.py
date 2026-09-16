import sys
from dotenv import load_dotenv
from google import genai
import os

load_dotenv()
sys.stdout.reconfigure(encoding="utf-8")

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

PROMPT = "Write a one-sentence creative description of Cambodia in English."
RUNS = 5  # How many times to repeat the same call

def test_repeat(label: str, config: dict, runs: int):
    print(f"\n{'='*60}")
    print(f"  TEST: {label}")
    print(f"  Config: {config}")
    print(f"  Running {runs}x with the SAME config...")
    print(f"{'='*60}")
    
    outputs = []
    for i in range(1, runs + 1):
        interaction = client.interactions.create(
            model="gemma-4-31b-it",
            input=PROMPT,
            generation_config=config,
        )
        text = interaction.output_text.strip()
        outputs.append(text)
        print(f"  Run {i}: {text}")
    
    # Check if all outputs are identical
    all_same = len(set(outputs)) == 1
    print(f"\n  RESULT: {'ALL SAME (deterministic!)' if all_same else f'DIFFERENT ({len(set(outputs))} unique answers)'}")
    print()


# Test 1: temperature=0 — should be deterministic
test_repeat(
    "temperature=0  (deterministic?)",
    {"temperature": 0.0, "top_p": 0.9, "top_k": 40},
    RUNS,
)

# Test 2: temperature=1 — should vary
test_repeat(
    "temperature=1  (varied?)",
    {"temperature": 1.0, "top_p": 0.9, "top_k": 40},
    RUNS,
)

print("Done!")
