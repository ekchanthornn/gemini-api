import sys
from dotenv import load_dotenv
from google import genai
import os

load_dotenv()
sys.stdout.reconfigure(encoding="utf-8")

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

PROMPT = "Write a one-sentence creative description of Cambodia in English."

# ─────────────────────────────────────────────
# Helper: run one interaction and print result
# ─────────────────────────────────────────────
def run_test(label: str, config: dict):
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"  Config: {config}")
    print(f"{'='*60}")
    interaction = client.interactions.create(
        model="gemini-3.5-flash-lite",
        input=PROMPT,
        generation_config=config,
    )
    print(f"  -> {interaction.output_text.strip()}")


# ─────────────────────────────────────────────
# 1. TEST temperature  (top_p & top_k fixed)
# ─────────────────────────────────────────────
print("\n\n[temperature]  controls randomness / creativity")
print("   Low  -> predictable, focused")
print("   High -> creative, varied\n")

for temp in [0.0, 0.5, 1.0, 2.0]:
    run_test(
        f"temperature = {temp}",
        {"temperature": temp, "top_p": 0.9, "top_k": 40},
    )

# ─────────────────────────────────────────────
# 2. TEST top_p  (temperature & top_k fixed)
# ─────────────────────────────────────────────
print("\n\n[top_p]  nucleus sampling - token pool size")
print("   Low  -> very focused, fewer word choices")
print("   High -> broader vocabulary\n")

for tp in [0.1, 0.5, 0.9, 1.0]:
    run_test(
        f"top_p = {tp}",
        {"temperature": 0.8, "top_p": tp, "top_k": 40},
    )

# ─────────────────────────────────────────────
# 3. TEST top_k  (temperature & top_p fixed)
# ─────────────────────────────────────────────
print("\n\n[top_k]  max candidate tokens per step")
print("   Low  -> very conservative word choices")
print("   High -> wider vocabulary\n")

for tk in [1, 10, 40, 100]:
    run_test(
        f"top_k = {tk}",
        {"temperature": 0.8, "top_p": 0.9, "top_k": tk},
    )

print("\n\nDone! Compare the outputs above to see each parameter's effect.\n")
