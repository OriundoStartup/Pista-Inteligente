import google.generativeai as genai
import os
import time
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Modelos candidatos para probar - ordenados por preferencia
# Actualizado 2026-01-21: Evitar -latest que migrará a Gemini 3 el 30/01/2026
candidates = [
    "gemini-2.0-flash",  # ✅ PREFERIDO: Versión estable
    "gemini-2.0-flash-001",
    "gemini-2.0-flash-lite-preview-02-05",
    "gemini-2.0-flash-lite-preview",
    "gemini-2.0-flash-exp",
    # Los siguientes alias cambiarán automáticamente el 30/01/2026 - evitar en producción:
    # "gemini-flash-latest",
    # "gemini-pro-latest"
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
