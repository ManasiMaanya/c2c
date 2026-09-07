import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is missing")

print("API key loaded.")

client = genai.Client(
    api_key=api_key,
    http_options=types.HttpOptions(
        timeout=30000,
    ),
)

print("Sending request...")

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents="Say hello.",
)

print("SUCCESS")
print(response.text)