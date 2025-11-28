import streamlit as st
import pandas as pd
import os
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import pago_link

# Importar módulos de la nueva arquitectura
from src.utils.helpers import load_css
from src.models.data_manager import cargar_datos, analizar_probabilidad_caballos
from src.views.chatbot_view import render_chatbot
from src.views.ads_view import render_ad_sidebar, render_ad_banner
from src.views.program_view import render_program_view

# Configuración de la página
st.set_page_config(
    page_title="Pista Inteligente: Análisis Hípico",
    page_icon="🐎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargar Estilos CSS Centralizados
css_content = load_css("styles/main.css")
st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

def main():
    # Verificar si existe el archivo de configuración de autenticación
    if not os.path.exists('auth_config.yaml'):
        # Crear archivo con configuración por defecto
        default_config = {
            'cookie': {'expiry_days': 30, 'key': 'random_signature_key', 'name': 'auth_cookie'},
            'credentials': {'usernames': {'jsmith': {'email': 'js@test.com', 'name': 'John Smith', 'password': '...'}}}
        }
        with open('auth_config.yaml', 'w') as file:
            yaml.dump(default_config, file, default_flow_style=False)

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
            
            # Banner Publicitario Principal (Top)
            render_ad_banner()

            st.markdown("---")

            # --- SIDEBAR ---
            with st.sidebar:
                # Logo en Sidebar
                logo_path = "logo_pista_inteligente.jpg"
                if os.path.exists(logo_path):
                    st.image(logo_path, width=200)
                
                st.header("⚙️ Filtros")
                df_all = cargar_datos()
                
                if not df_all.empty:
                    hipodromos = ['Todos'] + sorted(df_all['hipodromo'].unique().tolist())
                    hipodromo_sel = st.selectbox("Selecciona Hipódromo:", hipodromos)
                    
                    st.markdown("---")
                    st.metric("Total Carreras", len(df_all))
                else:
                    hipodromo_sel = 'Todos'
                    st.warning("Sin datos disponibles")
                
                # Renderizar Publicidad en Sidebar
                render_ad_sidebar()

            # --- DASHBOARD ---
            if df_all.empty:
                st.warning("⚠️ No hay datos disponibles. Ejecuta analisis.py")
                return

            df = df_all if hipodromo_sel == 'Todos' else df_all[df_all['hipodromo'] == hipodromo_sel]

            # KPIs
            c1, c2, c3 = st.columns(3)
            c1.metric("🏇 Carreras Filtradas", len(df))
            c2.metric("🎯 Patrones Únicos", df['llegada_str'].nunique())
            conteo = df['llegada_str'].value_counts()
            c3.metric("🔄 Patrones Repetidos", len(conteo[conteo > 1]))

            st.markdown("---")

            # TABS
            tab1, tab2, tab3, tab4 = st.tabs(["🚨 Patrones a Vigilar", "📈 Análisis Completo", "📺 Teletrack Live", "🔮 Jornada Próxima"])

            with tab1:
                st.markdown("## 🚨 Patrones de Alta Frecuencia")
                es_premium = (st.session_state["username"] == 'admin_premium')
                
                if not es_premium:
                    st.warning("🔒 Contenido Exclusivo para Suscriptores Premium")
                    if st.button("Desbloquear Acceso Premium", type="primary"):
                        st.markdown(f'<meta http-equiv="refresh" content="0;url={pago_link.URL_PAGO}">', unsafe_allow_html=True)
                else:
                    patrones_alerta = conteo[conteo >= 3]
                    if not patrones_alerta.empty:
                        st.success('¡Análisis Confirmado! A COBRAR LOS QUE SABEN.')
                        st.dataframe(patrones_alerta, width='stretch')
                    else:
                        st.info("No hay patrones con 3+ repeticiones.")

            with tab2:
                st.markdown("## 📈 Todos los Patrones Repetidos")
                st.dataframe(conteo[conteo > 1], width='stretch')

            with tab3:
                st.markdown("## 📺 Teletrack / Carreras en Vivo")
                st.info("Transmisión en vivo próximamente.")

            with tab4:
                render_program_view()

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
            st.warning('Por favor, ingresa tus credenciales')

    except Exception as e:
        st.error(f"Error: {e}")

if __name__ == "__main__":
    main()
