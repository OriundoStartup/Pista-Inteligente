import streamlit as st
from src.models.data_manager import obtener_patrones_la_tercera

def render_patterns_view():
    """Renderiza la sección 'La Tercera es la Vencida'."""
    
    st.markdown("## 🎯 La Tercera es la Vencida")
    st.markdown("Estos patrones se han repetido **2 veces** en la historia. Estadísticamente, están a punto de ocurrir por tercera vez.")
    
    patrones = obtener_patrones_la_tercera()
    
    if not patrones:
        st.info("No hay patrones con exactamente 2 repeticiones en este momento.")
        return

    # Mostrar métricas resumen
    col1, col2 = st.columns(2)
    col1.metric("Oportunidades Detectadas", len(patrones))
    col2.metric("Mejor Probabilidad", f"{patrones[0]['probabilidad']}%" if patrones else "0%")
    
    st.markdown("---")
    
    # Grid de Patrones
    cols = st.columns(3)
    
    for idx, p in enumerate(patrones):
        with cols[idx % 3]:
            # Color de la barra de probabilidad
            color_bar = "#00ff00" if p['probabilidad'] > 80 else "#ffaa00" if p['probabilidad'] > 50 else "#ff4b4b"
            
            # Formatear números del patrón
            numeros = p['patron'].split('-')
            html_numeros = "".join([f'<span class="pattern-number">{n}</span>' for n in numeros])
            
            st.markdown(f"""
            <div class="pattern-card">
                <div class="pattern-header">
                    <span class="pattern-badge">🔥 OPORTUNIDAD</span>
                    <span style="color: {color_bar}; font-weight: bold;">{p['probabilidad']}% Prob.</span>
                </div>
                <div style="text-align: center; margin: 15px 0;">
                    <div class="pattern-numbers-container">
                        {html_numeros}
                    </div>
                    <div style="font-size: 12px; color: #888; margin-top: 5px;">Patrón de Llegada</div>
                </div>
                <div class="pattern-details">
                    <p><strong>Última vez:</strong> {p['ultima_fecha']}</p>
                    <p><strong>Hipódromo:</strong> {p['hipodromo']}</p>
                </div>
                <div class="probability-bar-bg">
                    <div class="probability-bar-fill" style="width: {p['probabilidad']}%; background: {color_bar};"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Detalles expandibles (Historial)
            with st.expander("📜 Ver Historial"):
                for h in p['historial']:
                    st.caption(f"📅 {h['fecha']} | 📍 {h['hipodromo']} | 🏁 Carrera {h['nro_carrera']}")
