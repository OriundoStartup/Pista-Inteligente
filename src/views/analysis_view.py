import streamlit as st
import pandas as pd
from src.models.data_manager import obtener_estadisticas_generales, obtener_top_quinelas

def render_analysis_view():
    """Renderiza el dashboard de análisis completo."""
    
    st.markdown("## 📈 Centro de Análisis Estadístico")
    st.markdown("Explora el rendimiento histórico de los números y descubre tendencias ocultas.")
    
    stats, df_numeros = obtener_estadisticas_generales()
    
    if not stats:
        st.warning("No hay suficientes datos para generar estadísticas.")
        return

    # KPIs Generales
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Carreras Analizadas", stats['total_carreras'])
    c2.metric("Hipódromos Monitoreados", stats['hipodromos'])
    c3.metric("Días de Data", stats['dias_registrados'])
    
    st.markdown("---")
    
    # Análisis de Números (Líderes)
    st.subheader("🏆 Rendimiento por Número de Partida")
    
    tab_win, tab_podio, tab_quinela = st.tabs(["🥇 Más Ganadores", "🏅 Más en Tabla (Top 3)", "🤝 Top Quinelas"])
    
    with tab_win:
        st.caption("Números que más veces han cruzado la meta en 1er lugar.")
        top_winners = df_numeros.sort_values('Victorias', ascending=False).head(10)
        st.bar_chart(top_winners.set_index('Numero')['Victorias'], color="#00ffff")
        
    with tab_podio:
        st.caption("Números más consistentes (1ro, 2do o 3ro).")
        top_podio = df_numeros.sort_values('Total Podios', ascending=False).head(10)
        st.bar_chart(top_podio.set_index('Numero')['Total Podios'], color="#00ff00")
        
    with tab_quinela:
        st.caption("Parejas de números que más se repiten en 1ro y 2do lugar (cualquier orden).")
        df_quinelas = obtener_top_quinelas()
        st.dataframe(df_quinelas, width='stretch', hide_index=True)

    st.markdown("---")
    
    # Sección Placeholder para Jinetes y Studs (Futura Expansión)
    st.subheader("🏇 Análisis de Profesionales (Beta)")
    st.info("ℹ️ La recolección de datos detallada de Jinetes, Preparadores y Studs está en proceso. Próximamente verás aquí sus estadísticas de rendimiento y ROI.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        <div style="opacity: 0.5; filter: blur(1px); pointer-events: none;">
            <h4>Top Jinetes (Demo)</h4>
            <ul>
                <li>J. Medina - 25% Win Rate</li>
                <li>B. Sancho - 18% Win Rate</li>
                <li>K. Espina - 15% Win Rate</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with col_b:
        st.markdown("""
        <div style="opacity: 0.5; filter: blur(1px); pointer-events: none;">
            <h4>Top Studs (Demo)</h4>
            <ul>
                <li>Stud Doña Sofia - $15M</li>
                <li>Stud Matriarca - $12M</li>
                <li>Stud Don Alberto - $10M</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

