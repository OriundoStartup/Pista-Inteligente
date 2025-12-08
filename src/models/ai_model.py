import google.generativeai as genai
import os

import time
from .data_manager import cargar_programa, obtener_analisis_jornada, obtener_estadisticas_generales

def generar_contexto_hipico():
    """Genera un string de contexto con predicciones y estadísticas."""
    contexto = []
    
    # 1. Predicciones del Programa Actual
    try:
        analisis = obtener_analisis_jornada()
        if analisis:
            contexto.append("📊 PREDICCIONES PARA EL PROGRAMA ACTUAL:")
            for carrera in analisis[:15]: # Limitar a primeras 15 para no saturar
                pred_str = ""
                # Tomar Top 3 predicciones
                top_preds = carrera.get('predicciones', [])[:3]
                if top_preds:
                    nombres = [f"{p['caballo']} (Score: {int(p['puntaje_ia'])})" for p in top_preds]
                    pred_str = ", ".join(nombres)
                
                contexto.append(f"- {carrera['hipodromo']} Carrera {carrera['nro_carrera']} ({carrera['distancia']}): Favoritos IA -> {pred_str}")
        else:
            contexto.append("No hay un programa cargado actualmente.")
    except Exception as e:
        contexto.append(f"Error cargando predicciones: {e}")

    # 2. Estadísticas Generales
    try:
        stats = obtener_estadisticas_generales()
        if isinstance(stats, dict):
            # Top Jinetes
            jinetes = stats.get('jinetes', [])[:5]
            if jinetes:
                top_j = ", ".join([f"{j['jinete']} ({j['eficiencia']:.1f}%)" for j in jinetes])
                contexto.append(f"\n🏆 MEJORES JINETES (Eficiencia): {top_j}")
            
            # Top Caballos
            caballos = stats.get('caballos', [])[:5]
            if caballos:
                top_c = ", ".join([f"{c['caballo']} ({c['ganadas']} wins)" for c in caballos])
                contexto.append(f"🐴 MEJORES CABALLOS RECIENTES: {top_c}")
    except Exception as e:
        contexto.append(f"Error cargando estadísticas: {e}")
        
    return "\n".join(contexto)

def get_gemini_response_stream(prompt, history=[]):
    """Obtiene respuesta del modelo Gemini con streaming y contexto hípico enriquecido."""
    try:
        # Generar Contexto Dinámico
        contexto_hipico = generar_contexto_hipico()
        
        # Configurar modelo
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # System Prompt Mejorado
        system_prompt = f"""
        Rol: Eres 'Caballo Roro', el analista experto de hípica chilena de la plataforma 'Pista Inteligente'.
        Objetivo: Asesorar a los usuarios usando las predicciones y estadísticas provistas.
        
        INFORMACIÓN EN TIEMPO REAL (Contexto):
        {contexto_hipico}
        
        Instrucciones:
        1. Si el usuario pregunta por una carrera específica, busca en el contexto las predicciones de la IA.
        2. Si no hay datos para una carrera, dilo honestamente ("No tengo datos para esa carrera en este momento").
        3. Se amable pero profesional. Usa terminología hípica (fija, golpe, dividendo).
        4. Tus predicciones y análisis se basan estrictamente en los datos provistos arriba.
        5. Siempre responde en Español Chileno neutro o técnico.
        """
        
        # Iniciar chat (si history es soportado, sino query directa)
        # Nota: Gemini API maneja history en start_chat object, pero flask pasa history list.
        # Por simplicidad en este MVP, inyectamos el prompt actual con el system prompt.
        
        chat = model.start_chat(history=history)
        
        full_prompt = f"{system_prompt}\n\nPREGUNTA DEL USUARIO: {prompt}"
        response = chat.send_message(full_prompt, stream=True)
        
        for chunk in response:
            if chunk.text:
                yield chunk.text
                
    except Exception as e:
        yield f"⚠️ Error analizando la carrera: {str(e)}"
