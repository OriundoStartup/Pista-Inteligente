import Link from 'next/link'
import type { Metadata } from 'next'
import PatronesList from '@/components/PatronesList'

export const metadata: Metadata = {
    title: 'Patrones de Carreras y Análisis con IA | Pista Inteligente',
    description: 'Descubre patrones estadísticos en las carreras de caballos de Chile. Análisis profundo con Inteligencia Artificial del Hipódromo Chile, Club Hípico, Valparaíso y Concepción.',
}

export default function AnalisisPage() {
    const patrones = [
        {
            titulo: 'Ventaja del Riel Interior',
            descripcion: 'Caballos que parten en posiciones interiores (partida 1 a 3) muestran una ventaja estadística en distancias cortas (800-1100m).',
            detalle: 'En distancias sprint, la posición de partida es crítica porque hay menos tiempo para recuperar terreno. Los caballos del riel interior recorren menos distancia en las curvas, lo que puede traducirse en un ahorro de entre 1 y 3 cuerpos al final. Este patrón es especialmente marcado en la pista de arena del Hipódromo Chile, donde la curva inicial es cerrada.',
            impacto: 'Alto'
        },
        {
            titulo: 'Factor Jinete-Caballo',
            descripcion: 'Combinaciones jinete-caballo con historial positivo previo mejoran significativamente las probabilidades de éxito.',
            detalle: 'Cuando un jinete ya ha montado y ganado con un caballo específico, existe un conocimiento mutuo que beneficia el rendimiento. El jinete conoce el temperamento del ejemplar, su ritmo ideal y cómo responde a las instrucciones. Nuestro modelo asigna un bonus a parejas jinete-caballo con al menos dos carreras previas exitosas juntos.',
            impacto: 'Alto'
        },
        {
            titulo: 'Descenso de Categoría',
            descripcion: 'Caballos que bajan de categoría respecto a su última carrera tienden a mostrar mejor rendimiento relativo.',
            detalle: 'Un caballo que compitió en una categoría superior y no obtuvo buenos resultados puede ser movido a una categoría inferior donde enfrenta rivales menos experimentados. Esto es análogo a un jugador de primera división compitiendo en segunda: su nivel de habilidad puede ser superior al promedio del grupo. Este factor es una de las señales más confiables para nuestro modelo.',
            impacto: 'Medio'
        },
        {
            titulo: 'Descanso Óptimo',
            descripcion: 'Los caballos con un período de descanso de 21 a 35 días entre carreras rinden mejor estadísticamente.',
            detalle: 'El descanso permite la recuperación muscular y mental del caballo. Períodos muy cortos (menos de 14 días) pueden indicar fatiga acumulada, mientras que períodos muy largos (más de 60 días) pueden señalar problemas de salud o pérdida de ritmo competitivo. El rango de 21-35 días es el punto óptimo donde el caballo está descansado pero mantiene su forma física competitiva.',
            impacto: 'Medio'
        },
        {
            titulo: 'Condición de Pista',
            descripcion: 'La superficie y condición de la pista (seca, húmeda, pesada) favorece determinados perfiles de caballos.',
            detalle: 'Existen caballos que son especialistas en pista pesada (húmeda) mientras que pierden rendimiento en pista rápida, y viceversa. Nuestro modelo analiza el historial de cada caballo segmentado por condición de pista para identificar estas preferencias. En la pista de arena del Hipódromo Chile, la condición afecta menos que en las pistas de pasto del Club Hípico y Valparaíso Sporting, donde la lluvia cambia radicalmente las condiciones.',
            impacto: 'Alto'
        },
    ]

    return (
        <>
            {/* Header with original content */}
            <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
                <h1 style={{ fontSize: 'clamp(1.75rem, 5vw, 2.5rem)', color: 'var(--text-main)', marginBottom: '0.5rem', fontWeight: 800 }}>
                    🔍 Patrones Detectados por IA en Carreras de Caballos
                </h1>
                <p style={{ color: 'var(--text-muted)', fontSize: '1.05rem', maxWidth: '800px', margin: '0 auto', lineHeight: 1.7 }}>
                    Nuestro sistema de Inteligencia Artificial analiza continuamente los resultados de carreras disputadas
                    en los hipódromos chilenos para detectar patrones estadísticos recurrentes. Estos patrones son factores
                    que nuestro modelo utiliza como variables predictivas para generar las predicciones diarias.
                </p>
            </div>

            {/* Introductory explanation */}
            <div className="glass-card" style={{ marginBottom: '1.5rem', padding: '1.5rem' }}>
                <h2 style={{ color: 'var(--text-main)', fontSize: '1.2rem', marginBottom: '0.75rem', fontWeight: 700 }}>
                    ¿Qué es un patrón estadístico en la hípica?
                </h2>
                <p style={{ color: 'var(--text-muted)', margin: 0, lineHeight: 1.7, fontSize: '0.95rem' }}>
                    Un patrón estadístico es una tendencia que se repite con frecuencia significativa a lo largo de múltiples
                    carreras y jornadas. No se trata de predicciones infalibles, sino de factores que, en combinación,
                    incrementan la probabilidad de un resultado. Por ejemplo, si un caballo descansó entre 21 y 35 días,
                    compite en una categoría inferior a la anterior y su jinete lo ha montado exitosamente antes, la
                    <strong> convergencia de estos tres factores</strong> genera una señal fuerte para nuestro modelo.
                    Individualmente, cada factor aporta información parcial; juntos, forman una predicción robusta.
                </p>
            </div>

            {/* Dynamic Patterns Section */}
            <div className="glass-card" style={{ marginBottom: '1.5rem' }}>
                <div className="section-title">🎰 Patrones Numéricos en Vivo</div>
                <p style={{ color: 'var(--text-muted)', marginBottom: '1rem', fontSize: '0.95rem', lineHeight: 1.6 }}>
                    Estos números (mandiles) han formado combinaciones ganadoras (Quinelas, Trifectas, Superfectas) al menos
                    2 veces en los últimos 60 días. Son tendencias observadas en los resultados reales, no proyecciones.
                </p>
                <PatronesList />
            </div>

            {/* Patrones Grid - Expanded with detailed explanations */}
            <div className="glass-card" style={{ marginBottom: '2rem' }}>
                <div className="section-title">📚 Factores Estadísticos que Analiza Nuestro Modelo</div>
                <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem', lineHeight: 1.7, fontSize: '0.95rem' }}>
                    A continuación describimos los cinco factores más influyentes que nuestro modelo de Machine Learning
                    utiliza para evaluar las probabilidades de cada caballo. Cada factor ha sido validado estadísticamente
                    con datos de más de 1.000 carreras disputadas en hipódromos chilenos.
                </p>

                <div style={{ display: 'grid', gap: '1.25rem' }}>
                    {patrones.map((patron, index) => (
                        <div
                            key={index}
                            className="glass-card"
                            style={{
                                borderLeft: `4px solid ${patron.impacto === 'Alto' ? 'var(--primary)' : 'var(--secondary)'}`,
                                padding: '1.5rem'
                            }}
                        >
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                                <h3 style={{ color: 'var(--text-main)', margin: 0, fontSize: '1.15rem' }}>{patron.titulo}</h3>
                                <span
                                    style={{
                                        background: patron.impacto === 'Alto' ? 'rgba(139, 92, 246, 0.2)' : 'rgba(6, 182, 212, 0.2)',
                                        color: patron.impacto === 'Alto' ? 'var(--primary)' : 'var(--secondary)',
                                        padding: '0.25rem 0.75rem',
                                        borderRadius: '20px',
                                        fontSize: '0.8rem',
                                        fontWeight: 600,
                                        whiteSpace: 'nowrap',
                                        marginLeft: '0.75rem'
                                    }}
                                >
                                    Impacto {patron.impacto}
                                </span>
                            </div>
                            <p style={{ color: 'var(--text-main)', margin: '0.5rem 0', fontWeight: 500, fontSize: '0.95rem' }}>{patron.descripcion}</p>
                            <p style={{ color: 'var(--text-muted)', margin: 0, lineHeight: 1.7, fontSize: '0.9rem' }}>{patron.detalle}</p>
                        </div>
                    ))}
                </div>
            </div>

            {/* How it Works - Expanded */}
            <div className="glass-card" style={{ marginBottom: '2rem' }}>
                <div className="section-title">🤖 ¿Cómo Funciona el Análisis de Patrones?</div>
                <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem', lineHeight: 1.7, fontSize: '0.95rem' }}>
                    Nuestro pipeline de análisis se ejecuta de forma automatizada cada vez que se disputa una jornada hípica.
                    El proceso consta de tres etapas fundamentales que transforman datos crudos en predicciones calibradas.
                </p>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem' }}>
                    <div style={{ padding: '1.5rem', background: 'rgba(52, 211, 153, 0.08)', borderRadius: '12px' }}>
                        <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem', textAlign: 'center' }}>📥</div>
                        <h3 style={{ color: 'var(--secondary)', marginBottom: '0.5rem', fontSize: '1.1rem', textAlign: 'center' }}>1. Recolección Automática</h3>
                        <p style={{ color: 'var(--text-muted)', margin: 0, lineHeight: 1.7, fontSize: '0.9rem' }}>
                            Nuestro sistema de scraping recopila automáticamente los programas de carreras publicados por los
                            hipódromos oficiales. Extraemos datos de partantes, jinetes, preparadores, distancias, pesos,
                            posiciones de partida y condiciones de pista. Los resultados se incorporan después de cada jornada.
                        </p>
                    </div>

                    <div style={{ padding: '1.5rem', background: 'rgba(99, 102, 241, 0.08)', borderRadius: '12px' }}>
                        <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem', textAlign: 'center' }}>🧮</div>
                        <h3 style={{ color: 'var(--primary)', marginBottom: '0.5rem', fontSize: '1.1rem', textAlign: 'center' }}>2. Feature Engineering</h3>
                        <p style={{ color: 'var(--text-muted)', margin: 0, lineHeight: 1.7, fontSize: '0.9rem' }}>
                            Transformamos los datos crudos en más de 50 variables predictivas. Este proceso incluye calcular
                            estadísticas rolling (eficiencia del jinete en los últimos N días), generar features de interacción
                            (combinación jinete-distancia), y aplicar encoding específico para variables categóricas de alta cardinalidad.
                        </p>
                    </div>

                    <div style={{ padding: '1.5rem', background: 'rgba(251, 191, 36, 0.08)', borderRadius: '12px' }}>
                        <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem', textAlign: 'center' }}>🎯</div>
                        <h3 style={{ color: 'var(--accent)', marginBottom: '0.5rem', fontSize: '1.1rem', textAlign: 'center' }}>3. Predicción Calibrada</h3>
                        <p style={{ color: 'var(--text-muted)', margin: 0, lineHeight: 1.7, fontSize: '0.9rem' }}>
                            Nuestro ensemble de LightGBM, XGBoost y CatBoost genera un Score de Confianza inicial.
                            Luego, un calibrador isotónico ajusta estas probabilidades para que reflejen la frecuencia
                            real de aciertos. El resultado es un ranking de caballos con probabilidades calibradas.
                        </p>
                    </div>
                </div>
            </div>

            {/* Disclaimer */}
            <div className="glass-card" style={{ marginBottom: '2rem', padding: '1.5rem', borderLeft: '4px solid var(--accent)' }}>
                <h3 style={{ color: 'var(--accent)', marginBottom: '0.5rem', fontSize: '1.05rem' }}>⚠️ Aviso Importante</h3>
                <p style={{ color: 'var(--text-muted)', margin: 0, lineHeight: 1.7, fontSize: '0.95rem' }}>
                    Los patrones estadísticos descritos en esta página son tendencias históricas observadas y <strong>no constituyen
                        garantías de resultados futuros</strong>. Las carreras de caballos son eventos deportivos con un componente
                    de incertidumbre inherente. Los patrones pueden cambiar con el tiempo a medida que nuevos datos se incorporan
                    al análisis. Utilice esta información como herramienta complementaria de análisis, no como única base para
                    decisiones financieras. Apueste siempre de forma responsable.
                </p>
            </div>

            {/* CTA */}
            <div style={{ textAlign: 'center', padding: '2rem 1rem', background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(52, 211, 153, 0.1))', borderRadius: '16px' }}>
                <h2 style={{ color: 'var(--text-main)', marginBottom: '1rem', fontSize: 'clamp(1.25rem, 4vw, 1.75rem)' }}>
                    Aprovecha estos patrones
                </h2>
                <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem', maxWidth: '500px', margin: '0 auto 1.5rem', lineHeight: 1.6 }}>
                    Nuestro modelo ya incorpora todos estos factores en las predicciones diarias. Consulta los pronósticos actualizados.
                </p>
                <Link href="/programa" className="cta-button" style={{ display: 'inline-block' }}>
                    Ver Predicciones de Hoy
                </Link>
            </div>
        </>
    )
}
