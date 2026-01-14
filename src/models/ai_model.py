import google.generativeai as genai
import os
from dotenv import load_dotenv
import time
from .data_manager import cargar_programa, obtener_analisis_jornada, obtener_estadisticas_generales

# Cargar variables de entorno desde .env
load_dotenv()

def configurar_gemini():
    """Configura la API key de Gemini desde variables de entorno.
    
    IMPORTANTE: Deshabilitamos Application Default Credentials para evitar
    conflictos con credenciales de gcloud que causan errores 403.
    """
    # Deshabilitar ADC (Application Default Credentials) que causa el error 403
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ""
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
        error_msg = """
╔══════════════════════════════════════════════════════════════════════╗
║              ⚠️  GEMINI_API_KEY NO CONFIGURADA  ⚠️                   ║
╚══════════════════════════════════════════════════════════════════════╝

Para usar las funcionalidades de IA, necesitas configurar tu API Key de Gemini:

📝 PASOS:
  1. Obtén tu API Key gratis en: https://makersuite.google.com/app/apikey
  2. Crea un archivo .env en la raíz del proyecto
  3. Agrega la línea: GEMINI_API_KEY=tu_clave_aquí
  4. Reinicia la aplicación

💡 TIP: Puedes usar .env.example como plantilla:
     copy .env.example .env  (en Windows)
     
🔒 IMPORTANTE: El archivo .env no se subirá a Git (está en .gitignore)
"""
        print(error_msg)
        # raise ValueError("GEMINI_API_KEY no configurada. Ver instrucciones arriba.")
        print("⚠️ Continuando sin soporte de IA... (No API Key)")
    else:
        # Configurar explícitamente con API key
        genai.configure(api_key=api_key)
        print("✅ Gemini configurado con API Key")


def generar_contexto_hipico():
    """Genera un string de contexto con predicciones y estadísticas."""
    contexto = []
    
    # 1. Predicciones del Programa Actual
    try:
        analisis = obtener_analisis_jornada()
        if analisis:
            total_carreras = len(analisis)
            contexto.append(f"📊 PREDICCIONES PARA EL PROGRAMA ACTUAL ({total_carreras} carreras en total):")
            for carrera in analisis:  # SIN LÍMITE - mostrar TODAS las carreras para datos precisos
                pred_str = ""
                # Tomar Top 3 predicciones
                top_preds = carrera.get('predicciones', [])[:3]
                if top_preds:
                    nombres = [f"{p['caballo']} (Score: {int(p['puntaje_ia'])})" for p in top_preds]
                    pred_str = ", ".join(nombres)
                
                contexto.append(f"- {carrera['hipodromo']} Carrera {carrera['carrera']} ({carrera['distancia']}): Favoritos IA -> {pred_str}")
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
        # Configurar Gemini al inicio (verifica API key)
        configurar_gemini()
        
        # Generar Contexto Dinámico
        contexto_hipico = generar_contexto_hipico()
        
        # Configurar modelo (Usando versión verificada por script)
        model = genai.GenerativeModel('gemini-flash-latest')
        
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
        
        # Iniciar chat con reintentos
        chat = model.start_chat(history=history)
        full_prompt = f"{system_prompt}\n\nPREGUNTA DEL USUARIO: {prompt}"

        max_retries = 3
        base_delay = 2

        for attempt in range(max_retries):
            try:
                response = chat.send_message(full_prompt, stream=True)
                for chunk in response:
                    if chunk.text:
                        yield chunk.text
                break # Éxito, salir del loop de reintentos
            
            except Exception as e:
                # Si es error de cuota (429) o servidor (503), reintentar
                error_str = str(e)
                if "429" in error_str or "503" in error_str:
                    if attempt < max_retries - 1:
                        sleep_time = base_delay * (2 ** attempt) # 2s, 4s, 8s
                        yield f"⏳ Servidor ocupado, reintentando en {sleep_time}s... "
                        time.sleep(sleep_time)
                        continue
                
                # Si no es recuperable o se acabaron los intentos, lanzar
                raise e
                
    except Exception as e:
        yield f"⚠️ Error analizando la carrera: {str(e)}"
