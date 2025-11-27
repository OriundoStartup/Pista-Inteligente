import streamlit as st
import pandas as pd
import sqlite3
import streamlit as st
import pandas as pd
import sqlite3
import os
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import pago_link

# Configuración de la página
st.set_page_config(
    page_title="Pista Inteligente: Análisis Hípico",
    page_icon="🐎",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
</style>
""", unsafe_allow_html=True)

import itertools

@st.cache_data(ttl=86400)
def cargar_datos(nombre_db='hipica_data.db'):
    """Carga los datos desde la base de datos SQLite."""
    if not os.path.exists(nombre_db):
        st.error(f"⚠️ Base de datos {nombre_db} no encontrada. Ejecuta primero analisis.py.")
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
    
    # Optimizacion: Solo considerar los top N caballos por rendimiento general para las combinaciones
    # para evitar combinaciones de caballos con 0 historial si hay muchos participantes
    caballos_con_historial = [c for c in caballos_jornada if stats_caballos[c]['top3'] > 0]
    
    # Si hay muy pocos con historial, usamos todos los participantes
    candidatos = caballos_con_historial if len(caballos_con_historial) >= 3 else caballos_jornada
    
    # Si aun asi son menos de 3, no se pueden hacer trifectas
    if len(candidatos) < 3:
        return pd.DataFrame()

    # Limitar candidatos a los top 8 para evitar explosión combinatoria si todos tienen historial
    # (8P3 = 336 combinaciones, manejable. 15P3 = 2730, también manejable pero mejor optimizar)
    candidatos.sort(key=lambda x: stats_caballos[x]['top3'], reverse=True)
    candidatos_top = candidatos[:8]

    for p in itertools.permutations(candidatos_top, 3):
        c1, c2, c3 = p
        
        # Score ponderado: Pesa más haber salido en esa posición específica
        # Se suma un pequeño factor del Top3 general para desempates
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
    
    # Crear DataFrame y ordenar
    if not combinaciones:
        return pd.DataFrame()
        
    df_comb = pd.DataFrame(combinaciones)
    df_comb = df_comb.sort_values('Score', ascending=False).head(5)
    
    return df_comb[['Combinación', '1º Lugar', '2º Lugar', '3º Lugar']]

def main():
    # Verificar si existe el archivo de configuración de autenticación
    if not os.path.exists('auth_config.yaml'):
        # Crear archivo con configuración por defecto
        default_config = {
            'cookie': {
                'expiry_days': 30,
                'key': 'random_signature_key',
                'name': 'auth_cookie'
            },
            'credentials': {
                'usernames': {
                    'jsmith': {
                        'email': 'js@test.com',
                        'name': 'John Smith',
                        'password': '$2b$12$RjM8Nf1lKj9G3z7M9K6/q.x/x/x/x/x/x/x/x/x/x/x/x'
                    },
                    'rpal': {
                        'email': 'rpal@test.com',
                        'name': 'Rebecca Pal',
                        'password': '$2b$12$Kk9G3z7M9K6/q.x/x/x/x/x/x/x/x/x/x/x/x/x/x/x/x'
                    }
                }
            }
        }
        
        with open('auth_config.yaml', 'w') as file:
            yaml.dump(default_config, file, default_flow_style=False)
            
        st.warning("⚠️ Se ha generado un archivo 'auth_config.yaml' por defecto. Por favor, actualiza las credenciales.")

    # Cargar configuración de autenticación
    try:
        with open('auth_config.yaml') as file:
            config = yaml.load(file, Loader=SafeLoader)
            
        authenticator = stauth.Authenticate(
            config['credentials'],
            config['cookie']['name'],
            config['cookie']['key'],
            config['cookie']['expiry_days']
        )

        # Login widget - PRIORIDAD: Primera función de renderizado
        authenticator.login(location='main')

        # Control de flujo estricto
        if st.session_state["authentication_status"]:
            # Si está autenticado, mostrar botón de logout en sidebar
            with st.sidebar:
                st.write(f'Bienvenido *{st.session_state["name"]}*')
                authenticator.logout('Logout', 'main')
                st.markdown("---")

            # --- INICIO DE LA APLICACIÓN PRINCIPAL ---
            # Header con Logo y Título
            col_logo, col_title = st.columns([1, 5])
            with col_logo:
                if os.path.exists("logo_caballo_pc.png"):
                    st.image("logo_caballo_pc.png", width=100)
            with col_title:
                st.title("🐎 Pista Inteligente: Análisis Hípico")
                st.markdown("*\"A cobrar los que saben.\" - Pista Inteligente*")
            
            st.markdown("---")

            # Sidebar - Logo y Filtros
            with st.sidebar:
                # Logo en sidebar - Primero que se ve
                logo_path = os.path.join(os.path.dirname(__file__), "logo_caballo_pc.png")
                if os.path.exists(logo_path):
                    try:
                        st.image(logo_path, width=180, use_container_width=False)
                        st.markdown("### 🐎 Pista Inteligente")
                        st.markdown("*Análisis Hípico*")
                        st.markdown("---")
                    except Exception as e:
                        st.warning(f"Logo no disponible: {e}")
                        st.markdown("### 🐎 Pista Inteligente")
                        st.markdown("*Análisis Hípico*")
                        st.markdown("---")
                else:
                    # Si no hay logo, mostrar solo el título
                    st.markdown("### 🐎 Pista Inteligente")
                    st.markdown("*Análisis Hípico*")
                    st.markdown("---")
                
                st.header("⚙️ Filtros")
                
                # Cargar datos para obtener opciones de filtro
                df_all = cargar_datos()
                
                if not df_all.empty:
                    hipodromos_disponibles = ['Todos'] + sorted(df_all['hipodromo'].unique().tolist())
                    hipodromo_seleccionado = st.selectbox(
                        "Selecciona Hipódromo:",
                        hipodromos_disponibles,
                        index=0
                    )
                    
                    st.markdown("---")
                    st.markdown("### 📊 Estadísticas Generales")
                    st.metric("Total Carreras", len(df_all))
                    st.metric("Hipódromos", df_all['hipodromo'].nunique())
                    st.metric("Fechas Analizadas", df_all['fecha'].nunique())
                else:
                    hipodromo_seleccionado = 'Todos'
                    st.warning("Sin datos disponibles")

            # Aplicar filtro
            if df_all.empty:
                st.warning("⚠️ No hay datos disponibles para analizar. Ejecuta `python analisis.py` primero.")
                return

            if hipodromo_seleccionado != 'Todos':
                df = df_all[df_all['hipodromo'] == hipodromo_seleccionado].copy()
            else:
                df = df_all.copy()

            # KPI Principal
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

            # Análisis de Patrones
            conteo = df['llegada_str'].value_counts()
            repetidos = conteo[conteo > 1]

            # Tabs para organizar contenido
            tab1, tab2, tab3, tab4 = st.tabs(["🚨 Patrones a Vigilar", "📈 Análisis Completo", "📺 Teletrack Live", "🔮 Jornada Próxima"])

            with tab1:
                st.markdown("## 🚨 Patrones de Alta Frecuencia")
                
                # Verificar si es usuario premium
                es_premium = (st.session_state["username"] == 'admin_premium')
                
                if not es_premium:
                    st.warning("🔒 Contenido Exclusivo para Suscriptores Premium")
                    st.markdown("### ¡A COBRAR LOS QUE SABEN! Accede a los 130 patrones completos.")
                    st.markdown("Los usuarios gratuitos solo tienen acceso limitado. Desbloquea todo el potencial de la Pista Inteligente.")
                    
                    if st.button("Desbloquear Acceso Premium", type="primary"):
                        st.markdown(f'<meta http-equiv="refresh" content="0;url={pago_link.URL_PAGO}">', unsafe_allow_html=True)
                        st.markdown(f"[Haz clic aquí si no eres redirigido]({pago_link.URL_PAGO})")
                else:
                    st.markdown("*Patrones que se han repetido **3 o más veces** - Mayor probabilidad de ocurrencia*")
                    
                    # Filtrar patrones con 3+ repeticiones
                    patrones_alerta = conteo[conteo >= 3]
                    
                    if not patrones_alerta.empty:
                        # Banner destacado cuando hay patrones de alta frecuencia
                        st.success('¡Análisis Confirmado! A COBRAR LOS QUE SABEN.')
                        # Preparar datos para la tabla de alerta
                        datos_alerta = []
                        for patron, cantidad in patrones_alerta.items():
                            coincidencias = df[df['llegada_str'] == patron]
                            ultima_fecha = coincidencias['fecha'].max()
                            
                            datos_alerta.append({
                                "🎯 Patrón (1-2-3)": patron,
                                "🔄 Total Repeticiones": cantidad,
                                "📅 Última Ocurrencia": ultima_fecha,
                                "🏇 Hipódromo(s)": ", ".join(coincidencias['hipodromo'].unique())
                            })
                        
                        df_alerta = pd.DataFrame(datos_alerta)
                        df_alerta = df_alerta.sort_values(by="🔄 Total Repeticiones", ascending=False)
                        
                        # Mostrar tabla destacada
                        st.markdown('<div class="alert-table">', unsafe_allow_html=True)
                        st.dataframe(
                            df_alerta,
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                "🔄 Total Repeticiones": st.column_config.NumberColumn(
                                    "🔄 Total Repeticiones",
                                    help="Número de veces que se repitió este patrón",
                                    format="%d ⚡"
                                )
                            }
                        )
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Detalles expandibles para cada patrón de alerta
                        st.markdown("### 📋 Detalles de Ocurrencias")
                        for patron in patrones_alerta.index:
                            coincidencias = df[df['llegada_str'] == patron]
                            with st.expander(f"🔍 Ver {len(coincidencias)} ocurrencias del patrón: **{patron}**"):
                                st.dataframe(
                                    coincidencias[['fecha', 'hipodromo', 'nro_carrera', 'llegada_str']],
                                    hide_index=True,
                                    use_container_width=True
                                )
                    else:
                        st.info("ℹ️ No hay patrones con 3 o más repeticiones en el conjunto de datos actual.")

            with tab2:
                st.markdown("## 📈 Todos los Patrones Repetidos")
                
                if repetidos.empty:
                    st.info("ℹ️ No se encontraron patrones repetidos en la muestra actual.")
                else:
                    # Tabla resumen
                    tabla_datos = []
                    for patron, cantidad in repetidos.items():
                        tabla_datos.append({
                            "Combinación (1-2-3)": patron,
                            "Repeticiones": cantidad
                        })
                    
                    df_tabla = pd.DataFrame(tabla_datos)
                    df_tabla = df_tabla.sort_values(by="Repeticiones", ascending=False)
                    
                    st.dataframe(df_tabla, use_container_width=True, hide_index=True)

                    # Detalles expandibles
                    st.markdown("### 📋 Detalle por Patrón")
                    for patron, cantidad in repetidos.items():
                        with st.expander(f"Ver detalle: {patron} ({cantidad} veces)"):
                            coincidencias = df[df['llegada_str'] == patron]
                            st.dataframe(
                                coincidencias[['fecha', 'hipodromo', 'nro_carrera', 'llegada_str']],
                                hide_index=True,
                                use_container_width=True
                            )

            with tab3:
                st.markdown("## 📺 Teletrack / Carreras en Vivo")
                st.markdown("*Transmisión vía YouTube o Plataforma Hípica Oficial*")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # Video embed (usando un video de ejemplo de carreras de caballos)
                    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Placeholder
                    st.video(video_url)
                    
                    st.markdown("""
                    ### 🎥 Canales Oficiales
                    - **Club Hípico de Santiago**: [Ver Canal](https://www.youtube.com/@clubhipico)
                    - **Hipódromo Chile**: [Ver Canal](https://www.youtube.com/@hipodromo_chile)
                    """)
                
                with col2:
                    st.markdown("### 🔴 Transmisión en Vivo")
                    
                    if st.button("🎬 Ver Club Hípico en Vivo", use_container_width=True):
                        st.markdown("[🔗 Abrir transmisión](https://www.clubhipico.cl/carreras/senal-en-vivo)")
                    
                    if st.button("🎬 Ver Hipódromo Chile en Vivo", use_container_width=True):
                        st.markdown("[🔗 Abrir transmisión](https://www.hipodromo.cl/carreras-senal-en-vivo)")
                    
                    st.markdown("---")
                    st.info("💡 **Tip**: Las transmisiones en vivo están disponibles durante los días de carrera.")

            with tab4:
                st.markdown("## 🔮 Jornada Próxima - Alertas de Patrones")
                st.markdown("*Detecta cuando patrones históricos repetidos se encuentran programados para la próxima jornada*")
                
                # Cargar datos del programa de la próxima jornada
                try:
                    conn = sqlite3.connect('hipica_data.db')
                    df_programa = pd.read_sql("SELECT * FROM programa_carreras", conn)
                    conn.close()
                    
                    if df_programa.empty:
                        st.warning("⚠️ No hay datos del programa de la próxima jornada. Ejecuta `python demo_programa.py` para cargar datos de ejemplo.")
                    else:
                        # Mostrar información general del programa
                        st.success(f"✅ Programa cargado: {len(df_programa)} carreras encontradas")
                        
                        # KPIs del programa
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("📅 Fechas Programadas", df_programa['fecha'].nunique())
                        with col2:
                            st.metric("🏇 Hipódromos", df_programa['hipodromo'].nunique())
                        with col3:
                            st.metric("🏁 Total Carreras", len(df_programa))
                        
                        st.markdown("---")
                        st.markdown("### 🚨 Alertas de Patrones Repetidos")
                        
                        # Obtener patrones repetidos históricos (con 2+ repeticiones)
                        conteo_patrones = df_all['llegada_str'].value_counts()
                        patrones_repetidos = conteo_patrones[conteo_patrones > 1]
                        
                        if patrones_repetidos.empty:
                            st.info("ℹ️ No hay patrones históricos repetidos en la base de datos.")
                        else:
                            # Lista para almacenar las alertas encontradas
                            alertas_encontradas = []
                            
                            # Para cada patrón repetido, verificar si los caballos están en el programa
                            for patron, cantidad_repeticiones in patrones_repetidos.items():
                                # Extraer los números del patrón (ej: "3-7-10" -> [3, 7, 10])
                                numeros_patron = patron.split('-')
                                numeros_patron_int = [int(num) for num in numeros_patron]
                                
                                # Buscar en cada carrera del programa
                                for idx, row_programa in df_programa.iterrows():
                                    caballos_carrera = row_programa['caballos'].split(',')
                                    caballos_carrera_int = [int(c.strip()) for c in caballos_carrera if c.strip().isdigit()]
                                    
                                    # Verificar si TODOS los números del patrón están en esta carrera
                                    if all(num in caballos_carrera_int for num in numeros_patron_int):
                                        # ¡ALERTA! Este patrón está presente en esta carrera
                                        alertas_encontradas.append({
                                            '🎯 Patrón': patron,
                                            '🔄 Veces Repetido': cantidad_repeticiones,
                                            '🏇 Hipódromo': row_programa['hipodromo'],
                                            '🏁 Carrera Nº': row_programa['nro_carrera'],
                                            '📅 Fecha': row_programa['fecha'],
                                            '🐎 Caballos en Carrera': row_programa['caballos']
                                        })
                            
                            # Mostrar las alertas
                            if alertas_encontradas:
                                st.success(f"🎯 **¡{len(alertas_encontradas)} ALERTA(S) DE PATRÓN DETECTADA(S)!**")
                                
                                # Mostrar cada alerta de forma destacada
                                for i, alerta in enumerate(alertas_encontradas, 1):
                                    with st.container():
                                        st.markdown(f"""
                                        <div style='background: linear-gradient(135deg, #ff4b4b 0%, #ff8c42 100%); 
                                                    padding: 20px; 
                                                    border-radius: 10px; 
                                                    border: 3px solid #ff6b6b; 
                                                    margin: 10px 0;
                                                    box-shadow: 0 4px 6px rgba(0,0,0,0.3);'>
                                            <h3 style='color: white; margin: 0;'>⚡ ALERTA #{i}</h3>
                                            <p style='color: white; font-size: 18px; margin: 10px 0;'>
                                                <strong>¡Patrón Detectado!</strong> Los caballos del patrón <strong style='font-size: 24px;'>{alerta['🎯 Patrón']}</strong> 
                                                están corriendo en la <strong>Carrera N° {alerta['🏁 Carrera Nº']}</strong> del 
                                                <strong>{alerta['🏇 Hipódromo']}</strong>
                                            </p>
                                            <p style='color: white; font-size: 14px; margin: 5px 0;'>
                                                📅 Fecha: {alerta['📅 Fecha']} | 🔄 Este patrón se ha repetido <strong>{alerta['🔄 Veces Repetido']}</strong> veces en el historial
                                            </p>
                                        </div>
                                        """, unsafe_allow_html=True)
                                        
                                        # Expandible con detalles adicionales
                                        with st.expander(f"🔍 Ver detalles de la Alerta #{i}"):
                                            st.markdown(f"**Patrón histórico:** {alerta['🎯 Patrón']}")
                                            st.markdown(f"**Hipódromo:** {alerta['🏇 Hipódromo']}")
                                            st.markdown(f"**Carrera Número:** {alerta['🏁 Carrera Nº']}")
                                            st.markdown(f"**Fecha programada:** {alerta['📅 Fecha']}")
                                            st.markdown(f"**Caballos participantes:** {alerta['🐎 Caballos en Carrera']}")
                                            st.markdown(f"**Repeticiones históricas:** {alerta['🔄 Veces Repetido']} veces")
                                            
                                            # Mostrar historial del patrón
                                            st.markdown("---")
                                            st.markdown("**📊 Historial de este patrón:**")
                                            patron_historico = df_all[df_all['llegada_str'] == alerta['🎯 Patrón']]
                                            st.dataframe(
                                                patron_historico[['fecha', 'hipodromo', 'nro_carrera', 'llegada_str']],
                                                use_container_width=True,
                                                hide_index=True
                                            )
                            else:
                                st.info("ℹ️ No se encontraron patrones históricos repetidos en las carreras programadas de la próxima jornada.")
                        
                        # Sección de Proyecciones Estadísticas
                        st.markdown("---")
                        st.markdown("### 🔬 Proyecciones Estadísticas de Carrera")
                        st.markdown("*Análisis basado en el rendimiento histórico de los caballos participantes*")

                        if not df_programa.empty:
                            # Selector de carrera para análisis detallado
                            opciones_carrera = []
                            mapa_carreras = {}
                            
                            # Ordenar por hipódromo y número de carrera
                            df_prog_sorted = df_programa.sort_values(['hipodromo', 'nro_carrera'])
                            
                            for idx, row in df_prog_sorted.iterrows():
                                key = f"{row['hipodromo']} - Carrera {row['nro_carrera']}"
                                opciones_carrera.append(key)
                                mapa_carreras[key] = row

                            carrera_seleccionada = st.selectbox("Selecciona una carrera para analizar:", opciones_carrera)

                            if carrera_seleccionada:
                                datos_carrera = mapa_carreras[carrera_seleccionada]
                                caballos_str = datos_carrera['caballos']
                                
                                try:
                                    # Parsear caballos
                                    caballos_lista = [int(c.strip()) for c in caballos_str.split(',') if c.strip().isdigit()]
                                    
                                    st.markdown(f"**🐎 Caballos participantes:** {', '.join(map(str, caballos_lista))}")
                                    
                                    with st.spinner("Calculando probabilidades..."):
                                        # Ejecutar análisis usando df_all (historial completo)
                                        df_proyecciones = analizar_probabilidad_caballos(caballos_lista, df_all)
                                    
                                    if not df_proyecciones.empty:
                                        st.markdown("#### 🏆 Top 5 Llegadas Ganadoras Probables")
                                        st.dataframe(
                                            df_proyecciones, 
                                            use_container_width=True,
                                            hide_index=True,
                                            column_config={
                                                "Combinación": st.column_config.TextColumn("🎯 Combinación", help="Trifecta probable"),
                                                "1º Lugar": st.column_config.NumberColumn("🥇 1º Lugar", format="%d"),
                                                "2º Lugar": st.column_config.NumberColumn("🥈 2º Lugar", format="%d"),
                                                "3º Lugar": st.column_config.NumberColumn("🥉 3º Lugar", format="%d"),
                                            }
                                        )
                                    else:
                                        st.warning("⚠️ No hay suficientes datos históricos para generar proyecciones confiables para estos caballos.")
                                        
                                except Exception as e:
                                    st.error(f"Error al procesar datos de la carrera: {e}")

                        # Mostrar programa completo
                        st.markdown("---")
                        st.markdown("### 📋 Programa Completo de la Próxima Jornada")
                        
                        # Filtro por hipódromo
                        hipodromos_programa = ['Todos'] + sorted(df_programa['hipodromo'].unique().tolist())
                        hipodromo_filtro = st.selectbox(
                            "Filtrar por Hipódromo:",
                            hipodromos_programa,
                            key="filtro_hipodromo_programa"
                        )
                        
                        if hipodromo_filtro != 'Todos':
                            df_programa_filtrado = df_programa[df_programa['hipodromo'] == hipodromo_filtro]
                        else:
                            df_programa_filtrado = df_programa
                        
                        # Mostrar tabla
                        st.dataframe(
                            df_programa_filtrado,
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                "fecha": st.column_config.DateColumn("📅 Fecha", format="YYYY-MM-DD"),
                                "hipodromo": st.column_config.TextColumn("🏇 Hipódromo"),
                                "nro_carrera": st.column_config.NumberColumn("🏁 Nº Carrera", format="%d"),
                                "caballos": st.column_config.TextColumn("🐎 Caballos Participantes")
                            }
                        )
                        
                except Exception as e:
                    st.error(f"❌ Error al cargar datos del programa: {e}")
                    st.info("💡 **Sugerencia**: Ejecuta `python demo_programa.py` para generar datos de ejemplo del programa.")

            # Footer
            st.markdown("---")
            st.markdown("""
            <div style='text-align: center; color: #666;'>
                <p>🐎 Pista Inteligente | Desarrollado por <a href="https://OriundoStartUpchile.com" target="_blank" style="color: #2dd4bf; text-decoration: none;">OriundoStartUpchile.com</a></p>
            </div>
            """, unsafe_allow_html=True)
        
        elif st.session_state["authentication_status"] is False:
            st.error('Usuario/Contraseña incorrectos')
        elif st.session_state["authentication_status"] is None:
            st.warning('Por favor, ingresa tus credenciales en la barra lateral')
            st.info("💡 Usuario Demo: demo_gratis / clave123 (si aplica)")

    except Exception as e:
        st.error(f"Error en autenticación: {e}")

if __name__ == "__main__":
    main()
