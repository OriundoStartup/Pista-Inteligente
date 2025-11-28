import google.generativeai as genai
import streamlit as st
from .data_manager import cargar_programa

def configurar_gemini():
    """Configura la API key de Gemini."""
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

def get_gemini_response(prompt):
    """Obtiene respuesta del modelo Gemini con contexto hípico."""
    try:
        # Contexto: Intentamos cargar el programa de la próxima jornada
        contexto_str = ""
        df_prog_chat = cargar_programa()
        
        if not df_prog_chat.empty:
            resumen = "Resumen del Programa:\n"
            for _, row in df_prog_chat.iterrows():
                resumen += f"Carrera {row['nro_carrera']} en {row['hipodromo']}: {row['caballos']}\n"
            contexto_str = f"Contexto Hípico Actualizado:\n{resumen}\n"
            
        model = genai.GenerativeModel('gemini-2.5-flash')
        full_prompt = f"{contexto_str}Eres 'HipoBot AI', un asistente experto en hípica chilena. Responde de forma amigable, corta y útil. Usuario: {prompt}"
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Error técnico: {e}"
