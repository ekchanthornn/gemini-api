import os
import requests
import tarfile
from dotenv import load_dotenv
load_dotenv()

env_id = "fd9304f2435e554fee869f62f83c6837"
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