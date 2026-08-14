import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

print("=== DAFTAR MODEL GEMINI YANG TERSEDIA DI AKUNMU ===")
try:
    for m in client.models.list():
        # Menampilkan model yang mendukung generate content
        if hasattr(m, 'supported_actions') and "generateContent" in m.supported_actions:
            print(f"- {m.name}")
        elif not hasattr(m, 'supported_actions'):
            print(f"- {m.name}")
except Exception as e:
    print(f"Error saat mengambil daftar model: {e}")