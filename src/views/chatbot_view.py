import streamlit as st
import os
from src.utils.helpers import get_base64_image
from src.models.ai_model import get_gemini_response, configurar_gemini

def render_chatbot():
    """Renderiza el componente completo del chatbot."""
    
    # 1. Configuración de Estado
    if "show_chat" not in st.session_state:
        st.session_state.show_chat = False
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # 2. Configurar IA
    configurar_gemini()

    # 3. Lógica de Interfaz
    logo_hipobot = "hipobot_logo.jpg"
    logo_b64 = get_base64_image(logo_hipobot)
    
    # Botón Toggle (Invisible pero funcional para Streamlit)
    col_control = st.columns(1)[0]
    with col_control:
        if st.button("Toggle Chat", key="chat_toggle_btn", help="Click para abrir/cerrar"):
            st.session_state.show_chat = not st.session_state.show_chat
            st.rerun()

    # Renderizar el botón visual (solo decoración HTML)
    if logo_b64:
        st.markdown(f"""
        <div class="floating-chat-btn">
            <img src="data:image/jpeg;base64,{logo_b64}">
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="floating-chat-btn" style="font-size: 30px;">
            🐴
        </div>
        """, unsafe_allow_html=True)

    # 4. Ventana de Chat
    if st.session_state.show_chat:
        # Contenedor visual del chat
        st.markdown("""
        <div class="chat-window">
            <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 15px; color: white; border-bottom: 1px solid #00ffff;">
                <strong>🐴 HipoBot AI</strong> <span style="font-size: 12px; float: right;">🟢 En Línea</span>
            </div>
            <div style="flex-grow: 1; background: #1a1c24;"></div>
        </div>
        """, unsafe_allow_html=True)
        
        # Hack para posicionar el contenido dentro de nuestra ventana CSS
        with st.sidebar:
            st.markdown("---") # Separador dummy
        
        # Usamos un contenedor fijo simulado
        chat_container = st.container()
        with chat_container:
            if not st.session_state.messages:
                st.session_state.messages.append({"role": "assistant", "content": "¡Hola! Soy HipoBot. ¿En qué te ayudo hoy?"})

            for msg in st.session_state.messages:
                with st.chat_message(msg["role"], avatar="🐴" if msg["role"] == "assistant" else None):
                    st.markdown(f"<div class='chat-message'>{msg['content']}</div>", unsafe_allow_html=True)

        # Input de chat
        if prompt := st.chat_input("Pregunta sobre hípica..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.spinner("Pensando..."):
                respuesta = get_gemini_response(prompt)
            st.session_state.messages.append({"role": "assistant", "content": respuesta})
            st.rerun()
