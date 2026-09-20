import os
import requests
import tarfile
from dotenv import load_dotenv
load_dotenv()

# env_id = "75fe9483ef1538fa6e395b29807369d6"
env_id = "584bb2c0eb30ce2585025b5ced9402f5"

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