import streamlit as st
import pandas as pd
from src.models.data_manager import obtener_analisis_jornada

def render_program_view():
    """Renderiza la vista de la próxima jornada con tarjetas modernas."""
    
    analisis = obtener_analisis_jornada()
    
    if not analisis:
        st.info("⚠️ No hay datos del programa disponibles. Asegúrate de haber ejecutado el scraper.")
        return

    st.markdown("## 🔮 Próxima Jornada: Análisis Inteligente")
    st.markdown("Predicciones basadas en rendimiento histórico y patrones de llegada.")
    
    # Agrupar por Hipódromo
    hipodromos = sorted(list(set(a['hipodromo'] for a in analisis)))
    
    for hipodromo in hipodromos:
        st.markdown(f"### 🏇 {hipodromo}")
        carreras_hipodromo = [c for c in analisis if c['hipodromo'] == hipodromo]
        
        # Grid de carreras (2 columnas)
        cols = st.columns(2)
        
        for idx, carrera in enumerate(carreras_hipodromo):
            with cols[idx % 2]:
                with st.container():
                    # Tarjeta de Carrera
                    st.markdown(f"""
                    <div class="race-card">
                        <div class="race-header">
                            <span class="race-number">#{carrera['carrera']}</span>
                            <span class="race-time">{carrera['fecha']}</span>
                        </div>
                        <div class="race-content">
                            <div class="race-horses">
                                <strong>🐎 Participantes ({len(carrera['caballos'])}):</strong><br>
                                <span style="font-size: 12px; color: #aaa;">
                                    {', '.join([f"{n} ({c})" for c, n in carrera['caballos'][:8]])}...
                                </span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Predicciones (DataFrame nativo para interactividad)
                    if not carrera['predicciones'].empty:
                        st.markdown("**🏆 Predicción IA:**")
                        st.dataframe(
                            carrera['predicciones'].head(3), 
                            hide_index=True,
                            width='stretch'
                        )
                    else:
                        st.warning("Datos insuficientes para predecir.")
                    
                    st.markdown("---")
