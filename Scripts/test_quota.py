import google.generativeai as genai
import os
import time
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Candidates from user's previous list
candidates = [
    "gemini-2.0-flash-lite-preview-02-05",
    "gemini-2.0-flash-lite-preview",
    "gemini-2.0-flash-exp",
    "gemini-2.0-flash-001",
    "gemini-flash-latest", # Often alias for 1.5 flash
    "gemini-pro-latest"
]

print("🔍 Probando cuotas de modelos...")

for model_name in candidates:
    print(f"\n👉 Probando: {model_name}")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hola, ¿funcionas?")
        print(f"✅ ÉXITO! {model_name} respondió: {response.text[:20]}...")
        print(f"!!! ELEGIDO: {model_name} !!!")
        break
    except Exception as e:
        print(f"❌ FALLÓ {model_name}: {e}")
        time.sleep(1)
