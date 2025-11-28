import streamlit as st

def render_ad_sidebar():
    """Renderiza publicidad vertical en el sidebar."""
    st.markdown("---")
    st.markdown("<div style='text-align: center; font-size: 10px; color: #666; margin-bottom: 5px;'>PUBLICIDAD</div>", unsafe_allow_html=True)
    
    # Ad 1: Teletrack
    st.markdown("""
    <div class="ad-container-sidebar">
        <div class="ad-badge">EN VIVO</div>
        <h3>📺 TELETRACK</h3>
        <p>No te pierdas ninguna carrera. Sigue la transmisión oficial.</p>
        <a href="https://www.teletrak.cl" target="_blank" class="ad-button">Ver Transmisión</a>
    </div>
    """, unsafe_allow_html=True)

    # Ad 2: Club Hípico / Hipódromo (Rotativo o fijo)
    st.markdown("""
    <div class="ad-container-sidebar" style="margin-top: 15px; border-color: #ff4b4b;">
        <div class="ad-badge" style="background: #ff4b4b;">APUESTAS</div>
        <h3>🏇 APUESTA OFICIAL</h3>
        <p>Juega responsablemente en los sitios autorizados.</p>
        <div style="display: flex; gap: 5px; justify-content: center; margin-top: 10px;">
            <span class="ad-tag">Club Hípico</span>
            <span class="ad-tag">Hipódromo Chile</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_ad_banner():
    """Renderiza un banner horizontal premium."""
    st.markdown("""
    <div class="ad-banner-horizontal">
        <div class="ad-content">
            <span class="ad-label">ESPACIO PATROCINADO</span>
            <div class="ad-text">
                <strong>🎰 ¿TE SIENTES CON SUERTE?</strong>
                <span>Las mejores cuotas para la jornada de hoy están en <strong>TELETRACK.CL</strong></span>
            </div>
            <a href="https://www.teletrak.cl" target="_blank" class="ad-cta">JUGAR AHORA</a>
        </div>
    </div>
    """, unsafe_allow_html=True)
