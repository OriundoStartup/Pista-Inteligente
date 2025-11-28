import streamlit as st
import pandas as pd
<<<<<<< HEAD
=======
import sqlite3
>>>>>>> a854cad (feat: Implementación de la vista de Análisis Público, Integración del Chatbot con Gemini y Banners de Publicidad Estática.)
import os
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import pago_link
import itertools
import google.generativeai as genai
from google.generativeai import types

# Importar módulos de la nueva arquitectura
from src.utils.helpers import load_css
from src.models.data_manager import cargar_datos, analizar_probabilidad_caballos
from src.views.chatbot_view import render_chatbot
from src.views.ads_view import render_ad_sidebar, render_ad_banner
from src.views.program_view import render_program_view
from src.views.patterns_view import render_patterns_view
from src.views.analysis_view import render_analysis_view

# Configuración de la página
st.set_page_config(
    page_title="Pista Inteligente: Análisis Hípico",
    page_icon="🐎",
    layout="wide",
    initial_sidebar_state="expanded"
)

<<<<<<< HEAD
# Cargar Estilos CSS Centralizados
css_content = load_css("styles/main.css")
st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
=======
# CSS personalizado para tema oscuro y estilos mejorados
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
    }
    .alert-table {
        background-color: #ff4b4b20;
        border: 2px solid #ff4b4b;
        border-radius: 10px;
        padding: 10px;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
    /* Estilos para banners publicitarios */
    .ad-banner-main {
        background-color: #1f2937;
        border: 1px solid #374151;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
        cursor: pointer;
        transition: transform 0.2s;
    }
    .ad-banner-main:hover {
        transform: scale(1.01);
        border-color: #60a5fa;
    }
    .ad-banner-sidebar {
        background-color: #1f2937;
        border: 1px solid #374151;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    .ad-text {
        color: #9ca3af;
        font-size: 0.8em;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 5px;
    }
    .ad-content {
        color: #f3f4f6;
        font-weight: bold;
        font-size: 1.1em;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE DATOS ---

@st.cache_data(ttl=86400)
def cargar_datos(nombre_db='hipica_data.db'):
    """Carga los datos desde la base de datos SQLite."""
    if not os.path.exists(nombre_db):
        return pd.DataFrame()
        
    try:
        conn = sqlite3.connect(nombre_db)
        df = pd.read_sql("SELECT * FROM resultados", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"❌ Error al cargar desde DB: {e}")
        return pd.DataFrame()

def analizar_probabilidad_caballos(caballos_jornada, historial_resultados):
    """
    Analiza probabilidades para los caballos de la jornada.
    Retorna un DataFrame con el Top 5 de combinaciones probables.
    """
    if historial_resultados.empty or not caballos_jornada:
        return pd.DataFrame()

    stats_caballos = {}
    
    # Calcular estadísticas para cada caballo participante
    for caballo in caballos_jornada:
        # Frecuencia en cada posición
        freq_1 = len(historial_resultados[historial_resultados['primero'] == caballo])
        freq_2 = len(historial_resultados[historial_resultados['segundo'] == caballo])
        freq_3 = len(historial_resultados[historial_resultados['tercero'] == caballo])
        
        total_top3 = freq_1 + freq_2 + freq_3
        
        stats_caballos[caballo] = {
            '1ro': freq_1,
            '2do': freq_2,
            '3ro': freq_3,
            'top3': total_top3
        }
        
    # Generar combinaciones (Trifectas)
    combinaciones = []
    
    # Optimizacion: Solo considerar los top N caballos por rendimiento general
    caballos_con_historial = [c for c in caballos_jornada if stats_caballos[c]['top3'] > 0]
    candidatos = caballos_con_historial if len(caballos_con_historial) >= 3 else caballos_jornada
    
    if len(candidatos) < 3:
        return pd.DataFrame()

    candidatos.sort(key=lambda x: stats_caballos[x]['top3'], reverse=True)
    candidatos_top = candidatos[:8]

    for p in itertools.permutations(candidatos_top, 3):
        c1, c2, c3 = p
        score = (stats_caballos[c1]['1ro'] * 5 + stats_caballos[c1]['top3']) + \
                (stats_caballos[c2]['2do'] * 3 + stats_caballos[c2]['top3']) + \
                (stats_caballos[c3]['3ro'] * 1 + stats_caballos[c3]['top3'])
                
        combinaciones.append({
            'Combinación': f"{c1}-{c2}-{c3}",
            'Score': score,
            '1º Lugar': c1,
            '2º Lugar': c2,
            '3º Lugar': c3
        })
    
    if not combinaciones:
        return pd.DataFrame()
        
    df_comb = pd.DataFrame(combinaciones)
    df_comb = df_comb.sort_values('Score', ascending=False).head(5)
    
    return df_comb[['Combinación', '1º Lugar', '2º Lugar', '3º Lugar']]
>>>>>>> a854cad (feat: Implementación de la vista de Análisis Público, Integración del Chatbot con Gemini y Banners de Publicidad Estática.)


def cargar_contexto_desde_db():
    """Carga datos reales desde la base de datos para el contexto del chatbot."""
    try:
        conn = sqlite3.connect('hipica_data.db')
        
        # Cargar resultados históricos recientes
        try:
            df_resultados = pd.read_sql("SELECT * FROM resultados ORDER BY fecha DESC LIMIT 100", conn)
        except:
            df_resultados = pd.DataFrame()
        
        # Cargar predicciones de ML
        try:
            df_predicciones = pd.read_sql("SELECT * FROM predicciones", conn)
        except:
            df_predicciones = pd.DataFrame()
        
        conn.close()
        
        # Construir contexto dinámico
        contexto = "# DATOS DE CARRERAS HÍPICAS - CHILE (DATOS REALES)\n\n"
        
        # Predicciones de ML (PRIORIDAD ALTA)
        if not df_predicciones.empty:
            contexto += "## 🔮 PREDICCIONES DE IA PARA HOY\n"
            for hipodromo in df_predicciones['hipodromo'].unique():
                df_hip = df_predicciones[df_predicciones['hipodromo'] == hipodromo]
                contexto += f"\n### {hipodromo}:\n"
                for carrera in sorted(df_hip['nro_carrera'].unique()):
                    top3 = df_hip[df_hip['nro_carrera'] == carrera].head(3)
                    caballos_pred = [f"{row['caballo']} ({row['prob_1ro']}% ganar)" for _, row in top3.iterrows()]
                    contexto += f"- Carrera {carrera}: {', '.join(caballos_pred)}\n"
        
        # Estadísticas de resultados históricos
        if not df_resultados.empty:
            contexto += "\n## ESTADÍSTICAS RECIENTES (ÚLTIMAS 100 CARRERAS)\n"
            # Agregar resumen simple
            top_ganadores = df_resultados['primero'].value_counts().head(5).to_dict()
            contexto += f"- Caballos más ganadores: {top_ganadores}\n"
        
        return contexto
        
    except Exception as e:
        return f"# DATOS DE CARRERAS HÍPICAS - CHILE\n\nError al cargar datos: {str(e)}"

def obtener_respuesta_gemini(model, pregunta, historial):
    """Obtiene respuesta de Gemini basada en el contexto y la pregunta."""
    try:
        # Cargar contexto dinámico desde la DB
        contexto_actual = cargar_contexto_desde_db()
        
        # Construir el prompt con contexto
        system_instruction = f"""
Eres "Caballo Roro", un asistente experto en carreras hípicas de Chile.

Tu función es ayudar a los usuarios con información sobre:
- Estadísticas de carreras y resultados históricos
- Programa de próximas carreras
- Análisis de patrones de llegada
- Recomendaciones basadas en datos reales

DEBES RESPONDER BASÁNDOTE PRINCIPALMENTE EN ESTOS DATOS REALES:
{contexto_actual}

Instrucciones:
1. Sé conciso y directo (máximo 3-4 líneas)
2. Usa emojis relevantes (🏇, 📊, 🏁, 🐎)
3. Si la pregunta no está relacionada con hípica, redirige amablemente al tema
4. Usa formato Markdown para resaltar información importante (**negrita**)
5. Siempre mantén un tono profesional pero amigable
6. Basa tus respuestas en los datos reales proporcionados
7. Si no tienes datos suficientes, indícalo claramente
"""
        
        chat = model.start_chat(history=historial)
        response = chat.send_message(system_instruction + "\n\nUsuario: " + pregunta)
        return response.text
        
    except Exception as e:
        return f"⚠️ Error al procesar tu pregunta: {str(e)}"

# --- MAIN APP ---

def main():
    # Verificar si existe el archivo de configuración de autenticación
    if not os.path.exists('auth_config.yaml'):
        default_config = {
            'cookie': {'expiry_days': 30, 'key': 'random_signature_key', 'name': 'auth_cookie'},
<<<<<<< HEAD
            'credentials': {'usernames': {'jsmith': {'email': 'js@test.com', 'name': 'John Smith', 'password': '...'}}}
=======
            'credentials': {
                'usernames': {
                    'jsmith': {'email': 'js@test.com', 'name': 'John Smith', 'password': 'xxx'},
                    'rpal': {'email': 'rpal@test.com', 'name': 'Rebecca Pal', 'password': 'xxx'}
                }
            }
>>>>>>> a854cad (feat: Implementación de la vista de Análisis Público, Integración del Chatbot con Gemini y Banners de Publicidad Estática.)
        }
        with open('auth_config.yaml', 'w') as file:
            yaml.dump(default_config, file, default_flow_style=False)

    # Cargar configuración de autenticación
    try:
        with open('auth_config.yaml', encoding='utf-8', errors='ignore') as file:
            config = yaml.safe_load(file)
            
        authenticator = stauth.Authenticate(
            config['credentials'],
            config['cookie']['name'],
            config['cookie']['key'],
            config['cookie']['expiry_days']
        )

        authenticator.login(location='main')

        if st.session_state["authentication_status"]:
            with st.sidebar:
                st.write(f'Bienvenido *{st.session_state["name"]}*')
                authenticator.logout('Logout', 'main')
                st.markdown("---")

            # --- HEADER ---
            col_logo, col_title = st.columns([1, 5])
            with col_logo:
                # Usar el nuevo logo subido por el usuario
                if os.path.exists("logo_pista_inteligente.jpg"):
                    st.image("logo_pista_inteligente.jpg", width=120)
                elif os.path.exists("logo_caballo_pc.png"):
                    st.image("logo_caballo_pc.png", width=100)
            with col_title:
                st.title("🐎 Pista Inteligente: Análisis Hípico")
                st.markdown("*\"A cobrar los que saben.\" - Pista Inteligente*")
            
<<<<<<< HEAD
            # Banner Publicitario Principal (Top)
            render_ad_banner()
=======
            # --- PUBLICIDAD: BANNER PRINCIPAL ---
            st.markdown("""
            <div class="ad-banner-main" onclick="window.open('https://www.clubhipico.cl', '_blank')">
                <div class="ad-text">Espacio Publicitario</div>
                <div class="ad-content">🏇 CLUB HÍPICO DE SANTIAGO - ¡Vive la emoción de las carreras! 🏇</div>
                <div style="font-size: 0.9em; color: #60a5fa; margin-top: 5px;">Haz clic para ver la programación oficial</div>
            </div>
            """, unsafe_allow_html=True)
>>>>>>> a854cad (feat: Implementación de la vista de Análisis Público, Integración del Chatbot con Gemini y Banners de Publicidad Estática.)

            st.markdown("---")

            # --- SIDEBAR ---
            with st.sidebar:
<<<<<<< HEAD
                # Logo en Sidebar
                logo_path = "logo_pista_inteligente.jpg"
                if os.path.exists(logo_path):
                    st.image(logo_path, width=200)
=======
                logo_path = os.path.join(os.path.dirname(__file__), "logo_caballo_pc.png")
                if os.path.exists(logo_path):
                    st.image(logo_path, width=180)
                
                # --- PUBLICIDAD SIDEBAR 1 ---
                st.markdown("""
                <div class="ad-banner-sidebar">
                    <div class="ad-text">Publicidad</div>
                    <div class="ad-content">📊 HIPOFORMO CHILE</div>
                    <div style="font-size: 0.8em; margin-top: 5px;">Datos expertos para ganadores</div>
                </div>
                """, unsafe_allow_html=True)
>>>>>>> a854cad (feat: Implementación de la vista de Análisis Público, Integración del Chatbot con Gemini y Banners de Publicidad Estática.)
                
                st.header("⚙️ Filtros")
                df_all = cargar_datos()
                
                if not df_all.empty:
<<<<<<< HEAD
                    hipodromos = ['Todos'] + sorted(df_all['hipodromo'].unique().tolist())
                    hipodromo_sel = st.selectbox("Selecciona Hipódromo:", hipodromos)
=======
                    hipodromos_disponibles = ['Todos'] + sorted(df_all['hipodromo'].unique().tolist())
                    hipodromo_seleccionado = st.selectbox("Selecciona Hipódromo:", hipodromos_disponibles, index=0)
>>>>>>> a854cad (feat: Implementación de la vista de Análisis Público, Integración del Chatbot con Gemini y Banners de Publicidad Estática.)
                    
                    st.markdown("---")
                    st.metric("Total Carreras", len(df_all))
                else:
                    hipodromo_sel = 'Todos'
                    st.warning("Sin datos disponibles")
                
<<<<<<< HEAD
                # Renderizar Publicidad en Sidebar
                render_ad_sidebar()

            # --- DASHBOARD ---
            if df_all.empty:
                st.warning("⚠️ No hay datos disponibles. Ejecuta analisis.py")
=======
                # --- PUBLICIDAD SIDEBAR 2 ---
                st.markdown("""
                <div class="ad-banner-sidebar">
                    <div class="ad-text">Publicidad</div>
                    <div class="ad-content">📺 TELETRACK</div>
                    <div style="font-size: 0.8em; margin-top: 5px;">Tu canal de hípica 24/7</div>
                </div>
                """, unsafe_allow_html=True)

            if df_all.empty:
                st.warning("⚠️ No hay datos disponibles. Ejecuta la automatización primero.")
>>>>>>> a854cad (feat: Implementación de la vista de Análisis Público, Integración del Chatbot con Gemini y Banners de Publicidad Estática.)
                return

            df = df_all if hipodromo_sel == 'Todos' else df_all[df_all['hipodromo'] == hipodromo_sel]

<<<<<<< HEAD
            # KPIs
            c1, c2, c3 = st.columns(3)
            c1.metric("🏇 Carreras Filtradas", len(df))
            c2.metric("🎯 Patrones Únicos", df['llegada_str'].nunique())
            conteo = df['llegada_str'].value_counts()
            c3.metric("🔄 Patrones Repetidos", len(conteo[conteo > 1]))

            st.markdown("---")

            # TABS
=======
            # --- KPIs ---
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="🏇 Carreras Filtradas", value=len(df))
            with col2:
                patrones_unicos = df['llegada_str'].nunique()
                st.metric(label="🎯 Patrones Únicos", value=patrones_unicos)
            with col3:
                conteo = df['llegada_str'].value_counts()
                repetidos = conteo[conteo > 1]
                st.metric(label="🔄 Patrones Repetidos", value=len(repetidos))

            st.markdown("---")

            # --- TABS ---
>>>>>>> a854cad (feat: Implementación de la vista de Análisis Público, Integración del Chatbot con Gemini y Banners de Publicidad Estática.)
            tab1, tab2, tab3, tab4 = st.tabs(["🚨 Patrones a Vigilar", "📈 Análisis Completo", "📺 Teletrack Live", "🔮 Jornada Próxima"])

            # TAB 1: Patrones a Vigilar
            with tab1:
<<<<<<< HEAD
=======
                st.markdown("## 🚨 Patrones de Alta Frecuencia")
>>>>>>> a854cad (feat: Implementación de la vista de Análisis Público, Integración del Chatbot con Gemini y Banners de Publicidad Estática.)
                es_premium = (st.session_state["username"] == 'admin_premium')
                
                if not es_premium:
                    st.warning("🔒 Contenido Exclusivo para Suscriptores Premium")
<<<<<<< HEAD
                    st.markdown("### 🎯 La Tercera es la Vencida")
                    st.markdown("Descubre los patrones que están a punto de repetirse por tercera vez.")
=======
                    st.markdown("### ¡A COBRAR LOS QUE SABEN! Accede a los 130 patrones completos.")
>>>>>>> a854cad (feat: Implementación de la vista de Análisis Público, Integración del Chatbot con Gemini y Banners de Publicidad Estática.)
                    if st.button("Desbloquear Acceso Premium", type="primary"):
                        st.markdown(f'<meta http-equiv="refresh" content="0;url={pago_link.URL_PAGO}">', unsafe_allow_html=True)
                else:
<<<<<<< HEAD
                    render_patterns_view()
=======
                    st.markdown("*Patrones que se han repetido **3 o más veces** - Mayor probabilidad de ocurrencia*")
                    patrones_alerta = conteo[conteo >= 3]
                    
                    if not patrones_alerta.empty:
                        st.success('¡Análisis Confirmado! A COBRAR LOS QUE SABEN.')
                        datos_alerta = []
                        for patron, cantidad in patrones_alerta.items():
                            coincidencias = df[df['llegada_str'] == patron]
                            datos_alerta.append({
                                "🎯 Patrón (1-2-3)": patron,
                                "🔄 Total Repeticiones": cantidad,
                                "📅 Última Ocurrencia": coincidencias['fecha'].max(),
                                "🏇 Hipódromo(s)": ", ".join(coincidencias['hipodromo'].unique())
                            })
                        
                        df_alerta = pd.DataFrame(datos_alerta).sort_values(by="🔄 Total Repeticiones", ascending=False)
                        st.dataframe(df_alerta, width='stretch', hide_index=True)
                    else:
                        st.info("ℹ️ No hay patrones con 3 o más repeticiones.")
>>>>>>> a854cad (feat: Implementación de la vista de Análisis Público, Integración del Chatbot con Gemini y Banners de Publicidad Estática.)

            # TAB 2: Todos los Patrones
            with tab2:
<<<<<<< HEAD
                render_analysis_view()

            with tab3:
                st.markdown("## 📺 Teletrack / Carreras en Vivo")
                st.info("Transmisión en vivo próximamente.")
=======
                st.markdown("## 📈 Todos los Patrones Repetidos")
                if repetidos.empty:
                    st.info("ℹ️ No se encontraron patrones repetidos.")
                else:
                    tabla_datos = [{"Combinación (1-2-3)": p, "Repeticiones": c} for p, c in repetidos.items()]
                    df_tabla = pd.DataFrame(tabla_datos).sort_values(by="Repeticiones", ascending=False)
                    st.dataframe(df_tabla, use_container_width=True, hide_index=True)

            # TAB 3: Teletrack
            with tab3:
                st.markdown("## 📺 Teletrack / Carreras en Vivo")
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
                with col2:
                    st.markdown("### 🔴 Transmisión en Vivo")
                    if st.button("🎬 Ver Club Hípico en Vivo", use_container_width=True):
                        st.markdown("[🔗 Abrir transmisión](https://www.clubhipico.cl/carreras/senal-en-vivo)")
                    if st.button("🎬 Ver Hipódromo Chile en Vivo", use_container_width=True):
                        st.markdown("[🔗 Abrir transmisión](https://www.hipodromo.cl/carreras-senal-en-vivo)")
>>>>>>> a854cad (feat: Implementación de la vista de Análisis Público, Integración del Chatbot con Gemini y Banners de Publicidad Estática.)

            # TAB 4: Predicciones ML
            with tab4:
<<<<<<< HEAD
                render_program_view()
=======
                st.markdown("## 🔮 Jornada Próxima - Predicciones IA")
                st.markdown("*Análisis predictivo basado en Machine Learning (Random Forest)*")
                
                try:
                    conn = sqlite3.connect('hipica_data.db')
                    df_predicciones = pd.read_sql("SELECT * FROM predicciones", conn)
                    conn.close()
                except:
                    df_predicciones = pd.DataFrame()
                
                if not df_predicciones.empty:
                    col_pred_1, col_pred_2 = st.columns([1, 2])
                    
                    with col_pred_1:
                        hipodromos_pred = df_predicciones['hipodromo'].unique()
                        hipodromo_sel = st.selectbox("📍 Selecciona Hipódromo:", hipodromos_pred)
                        
                        carreras_pred = sorted(df_predicciones[df_predicciones['hipodromo'] == hipodromo_sel]['nro_carrera'].unique())
                        carrera_sel = st.selectbox("🏁 Selecciona Carrera:", carreras_pred, format_func=lambda x: f"Carrera {x}")
                        
                        st.info("🧠 Estas predicciones son generadas por un modelo Random Forest entrenado con resultados históricos.")

                    with col_pred_2:
                        st.markdown(f"**📊 Probabilidades para {hipodromo_sel} - Carrera {carrera_sel}**")
                        
                        df_display = df_predicciones[
                            (df_predicciones['hipodromo'] == hipodromo_sel) & 
                            (df_predicciones['nro_carrera'] == carrera_sel)
                        ].copy()
                        
                        df_display = df_display[['caballo', 'prob_1ro', 'prob_figuracion']]
                        df_display.columns = ['Caballo', 'Prob. Ganar', 'Prob. Figuración']
                        df_display = df_display.sort_values('Prob. Ganar', ascending=False)
                        
                        st.dataframe(
                            df_display, 
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                "Prob. Ganar": st.column_config.ProgressColumn(
                                    "Prob. Ganar", format="%.1f%%", min_value=0, max_value=100
                                ),
                                "Prob. Figuración": st.column_config.ProgressColumn(
                                    "Prob. Figuración", format="%.1f%%", min_value=0, max_value=100
                                )
                            }
                        )
                else:
                    st.warning("⚠️ No hay predicciones disponibles. Ejecuta la automatización.")

            # --- CHATBOT FLOTANTE (Floating Action Button) ---
            
            # Función para cargar imagen en base64
            import base64
            def get_base64_image(image_path):
                try:
                    with open(image_path, "rb") as img_file:
                        return base64.b64encode(img_file.read()).decode()
                except:
                    return ""

            # Cargar imagen del jinete
            jinete_b64 = get_base64_image("jinete_ai.png")
            
            # CSS Reforzado con Imagen de Fondo
            st.markdown(f"""
            <style>
                /* Forzar visibilidad del contenedor del popover */
                [data-testid="stPopover"] {{
                    display: block !important;
                    visibility: visible !important;
                    position: fixed !important;
                    bottom: 30px !important;
                    right: 30px !important;
                    z-index: 999999 !important;
                    background-color: transparent !important;
                    width: auto !important;
                    height: auto !important;
                }}
                
                /* Estilo del botón del popover */
                [data-testid="stPopover"] > div > button {{
                    width: 80px !important;
                    height: 80px !important;
                    border-radius: 50% !important;
                    background-color: #1f2937 !important;
                    background-image: url('data:image/png;base64,{jinete_b64}') !important;
                    background-size: cover !important;
                    background-position: center !important;
                    border: 3px solid #667eea !important;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.5) !important;
                    color: transparent !important; /* Ocultar el texto del botón */
                    transition: all 0.3s ease !important;
                    animation: pulse-animation 2s infinite !important;
                }}
                
                /* Hover effect */
                [data-testid="stPopover"] > div > button:hover {{
                    transform: scale(1.1) !important;
                    box-shadow: 0 8px 25px rgba(0,0,0,0.6) !important;
                    border-color: #764ba2 !important;
                }}
                
                /* Etiqueta "Ayuda" flotante */
                .chat-label {{
                    position: fixed;
                    bottom: 50px;
                    right: 120px;
                    background-color: white;
                    color: #333;
                    padding: 5px 12px;
                    border-radius: 20px;
                    font-weight: bold;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                    z-index: 999998;
                    pointer-events: none;
                    animation: float-label 3s ease-in-out infinite;
                    font-size: 0.9em;
                }}
                
                .chat-label::after {{
                    content: "";
                    position: absolute;
                    top: 50%;
                    right: -6px;
                    margin-top: -6px;
                    border-width: 6px;
                    border-style: solid;
                    border-color: transparent transparent transparent white;
                }}

                @keyframes pulse-animation {{
                    0% {{ box-shadow: 0 0 0 0 rgba(118, 75, 162, 0.7); }}
                    70% {{ box-shadow: 0 0 0 20px rgba(118, 75, 162, 0); }}
                    100% {{ box-shadow: 0 0 0 0 rgba(118, 75, 162, 0); }}
                }}
                
                @keyframes float-label {{
                    0%, 100% {{ transform: translateX(0); }}
                    50% {{ transform: translateX(-5px); }}
                }}
                
                /* Ajuste del contenido del popover */
                div[data-testid="stPopoverBody"] {{
                    width: 380px !important;
                    max-height: 550px !important;
                    border-radius: 15px !important;
                    border: 1px solid #4b5563 !important;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.5) !important;
                }}
            </style>
            
            <div class="chat-label">¡Ayuda Roro! 🏇</div>
            """, unsafe_allow_html=True)

            # Implementación del Chatbot
            if "messages" not in st.session_state:
                st.session_state.messages = []

            # Usamos un espacio en blanco para el botón porque la imagen está en el fondo CSS
            with st.popover(" ", use_container_width=False):
                # Header del chat con imagen y nombre
                col_chat_img, col_chat_title = st.columns([1, 3])
                with col_chat_img:
                    if os.path.exists("jinete_ai.png"):
                        st.image("jinete_ai.png", width=60)
                    else:
                        st.write("🏇")
                with col_chat_title:
                    st.markdown("### Caballo Roro")
                    st.caption("Tu experto hípico")
                
                st.markdown("---")
                
                # Contenedor para mensajes con scroll
                chat_container = st.container(height=400)
                with chat_container:
                    if not st.session_state.messages:
                        st.info("👋 ¡Hola! Soy Caballo Roro. Pregúntame sobre favoritos, estadísticas o el programa de hoy.")
                    
                    for message in st.session_state.messages:
                        with st.chat_message(message["role"]):
                            st.markdown(message["content"])

                # Input de chat
                if prompt := st.chat_input("Escribe tu pregunta aquí..."):
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    with chat_container:
                        with st.chat_message("user"):
                            st.markdown(prompt)

                        with st.chat_message("assistant"):
                            with st.spinner("Roro está pensando..."):
                                model = inicializar_gemini()
                                if model:
                                    # Convertir historial para Gemini
                                    historial_gemini = []
                                    for m in st.session_state.messages[:-1]:
                                        role = "user" if m["role"] == "user" else "model"
                                        historial_gemini.append({"role": role, "parts": [m["content"]]})
                                    
                                    response = obtener_respuesta_gemini(model, prompt, historial_gemini)
                                    st.markdown(response)
                                    st.session_state.messages.append({"role": "assistant", "content": response})
                                else:
                                    st.error("Error al conectar con Caballo Roro")
>>>>>>> a854cad (feat: Implementación de la vista de Análisis Público, Integración del Chatbot con Gemini y Banners de Publicidad Estática.)

            # Footer
            st.markdown("---")
            st.markdown("""
            <div style='text-align: center; color: #666;'>
                <p>🐎 Pista Inteligente | Desarrollado por <a href="https://OriundoStartUpchile.com" target="_blank" style="color: #2dd4bf; text-decoration: none;">OriundoStartUpchile.com</a></p>
            </div>
            """, unsafe_allow_html=True)

            # --- RENDERIZAR CHATBOT (VISTA) ---
            render_chatbot()

        elif st.session_state["authentication_status"] is False:
            st.error('Usuario/Contraseña incorrectos')
        elif st.session_state["authentication_status"] is None:
<<<<<<< HEAD
            st.warning('Por favor, ingresa tus credenciales')
=======
            st.warning('Por favor, ingresa tus credenciales en la barra lateral')
>>>>>>> a854cad (feat: Implementación de la vista de Análisis Público, Integración del Chatbot con Gemini y Banners de Publicidad Estática.)

    except Exception as e:
        st.error(f"Error: {e}")

if __name__ == "__main__":
    main()
