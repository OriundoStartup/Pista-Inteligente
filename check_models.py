import google.generativeai as genai
import os
import streamlit as st

# Intentar obtener la API key de los secretos de Streamlit o variable de entorno
try:
    # Simular carga de secretos si estuviéramos en el script principal
    # Para este script aislado, necesitamos que el usuario la provea o la lea de secrets.toml manualmente
    # Vamos a intentar leer el secrets.toml directamente
    import toml
    secrets = toml.load(".streamlit/secrets.toml")
    api_key = secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    
    print("Listando modelos disponibles...")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
            
except Exception as e:
    print(f"Error: {e}")
