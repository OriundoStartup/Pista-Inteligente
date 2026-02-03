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
            
            # Resumen por Hipódromo
            carreras_por_hipodromo = {}
            for c in analisis:
                h = c['hipodromo']
                carreras_por_hipodromo[h] = carreras_por_hipodromo.get(h, 0) + 1
            
            resumen_str = ", ".join([f"{h} ({n} carreras)" for h, n in carreras_por_hipodromo.items()])
            contexto.append(f"📊 RESUMEN JORNADA: Se detectaron carreras en: {resumen_str}")
            
            contexto.append(f"📋 DETALLE DE PREDICCIONES ({total_carreras} carreras disponibles):")
            for carrera in analisis:  # SIN LÍMITE - mostrar TODAS las carreras para datos precisos
                pred_str = ""
                # Tomar Top 3 predicciones
                top_preds = carrera.get('predicciones', [])[:3]
                if top_preds:
                    nombres = [f"{p['caballo']} (Score: {int(p['puntaje_ia'])})" for p in top_preds]
                    pred_str = ", ".join(nombres)
                
                contexto.append(f"- {carrera['hipodromo']} {carrera['carrera']}ª ({carrera['hora']} | {carrera['distancia']}m {carrera['pista']}): 🔮 {pred_str}")
        else:
            contexto.append("⚠️ No hay un programa de carreras cargado con predicciones actualmente.")
            contexto.append("Nota: Esto puede deberse a que no hay carreras hoy o el sistema de predicción se está actualizando.")
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
        
        # Obtener lista de todos los hipódromos soportados
        from .data_manager import obtener_lista_hipodromos
        hipodromos_soportados = obtener_lista_hipodromos()
        
        # Configurar modelo (Usando versión verificada por script)
        # Usar modelo estable en lugar de alias -latest para evitar cambios automáticos
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # System Prompt Mejorado - Rol Senior & Contexto Global
        system_prompt = f"""
        Rol: Eres 'Caballo Roro', el analista senior y experto de hípica chilena de la plataforma 'Pista Inteligente'.
        
        OBJETIVO PRINCIPAL:
        Entregar información precisa, profesional y estratégica a los usuarios, utilizando TODOS los datos disponibles de los hipódromos. Tu misión es ser el asistente definitivo para el hípico.

        CONTEXTO ACTUAL (DATOS EN TIEMPO REAL):
        --------------------------------------------------
        {contexto_hipico}
        --------------------------------------------------
        
        HIPÓDROMOS SOPORTADOS EN EL SISTEMA:
        {", ".join(hipodromos_soportados)}

        INSTRUCCIONES CLAVES:
        1. **Cobertura Total**: Siempre verifica y menciona información de todos los hipódromos disponibles en el contexto (Club Hípico, Hipódromo Chile, Sporting, Concepción). No te limites a uno solo a menos que el usuario lo pida.
        2. **Precisión**: Si el usuario pregunta por una carrera específica, usa los puntajes de IA y probabilidades del contexto. Si no hay datos, indícalo claramente.
        3. **Formato Profesional**: Usa listas, negritas y emojis estratégicos para hacer la lectura fácil y rápida.
           - Ejemplo: "🏆 **Fija del Día**: [Caballo]"
        4. **Lenguaje Hípico**: Habla como un experto. Usa términos como "fija", "golpe", "quinela", "índice", "preparador".
        5. **Honestidad de Datos**: Nunca inventes predicciones. Si el contexto dice "No hay un programa cargado", informa al usuario que estamos esperando la actualización del programa oficial.
        6. **Tono**: Amable, chileno neutro, alentador pero responsable (juego responsable).
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
