from dotenv import load_dotenv
from google import genai
import os

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


interaction = client.interactions.create(
    agent="antigravity-preview-05-2026",
    input="Write a Python script that generates the first 20 Fibonacci numbers and saves them to fibonacci.txt. Then read the file and print its contents.",
    environment="remote",
)
print(f"Environment: {interaction.environment_id}")

# interaction = client.interactions.create(
#     agent="antigravity-preview-05-2026",
#     input="សង្ខេបអត្ថបទចុងក្រោយរបស់ https://freshnewsasia.com បន្ទាប់មកផ្ញើរទៅកាន់ បង្កើត file 1.txt រក្សាទុកអត្ថបទសង្ខេបនេះ",
#     environment="remote",
# )
# print(f"Environment: {interaction.environment_id}")

print(interaction.output_text)