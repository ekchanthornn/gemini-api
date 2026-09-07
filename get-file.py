import os
import requests
import tarfile
from dotenv import load_dotenv
load_dotenv()

env_id = "c418fe9d4bf800578b57bf5f553f2f11"
api_key = os.getenv("GEMINI_API_KEY")

url = (
    f"https://generativelanguage.googleapis.com/v1beta/"
    f"files/environment-{env_id}:download"
)

response = requests.get(
    url,
    params={"alt": "media"},
    headers={"x-goog-api-key": api_key},
)

with open("snapshot.tar", "wb") as f:
    f.write(response.content)

with tarfile.open("snapshot.tar") as tar:
    tar.extractall("environment_files")

print("Downloaded!")