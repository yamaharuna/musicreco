import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    print("✅ GOOGLE_API_KEY is set:", api_key[:6] + "******")
else:
    print("❌ GOOGLE_API_KEY is NOT set. Check your .env file.")
