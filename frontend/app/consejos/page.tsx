import type { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
    title: 'Consejos de Análisis Hípico | Mejora tus Estrategias de Apuesta con IA',
    description: 'Aprende a analizar carreras de caballos como un profesional. Consejos sobre gestión de presupuesto, interpretación de datos de IA y estrategias para el Hipódromo Chile y Club Hípico.',
}

export default function ConsejosPage() {
    return (
        <div className="container" style={{ padding: '2rem 0' }}>
            <article style={{ maxWidth: '800px', margin: '0 auto' }}>
                <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
                    <h1 style={{ fontSize: 'clamp(1.75rem, 5vw, 2.5rem)', color: 'var(--text-main)', marginBottom: '0.75rem', fontWeight: 800 }}>
                        💡 Consejos para el Análisis Hípico Profesional
                    </h1>
                    <p style={{ color: 'var(--text-muted)', fontSize: '1.1rem', maxWidth: '700px', margin: '0 auto', lineHeight: 1.7 }}>
                        Combinar la intuición hípica con los datos de Inteligencia Artificial es la clave del éxito.
                        A continuación, compartimos estrategias y consejos fundamentales para elevar tu nivel de análisis.
                    </p>
                </div>

                <div className="glass-card" style={{ padding: '2rem', marginBottom: '1.5rem' }}>
                    <h2 style={{ color: 'var(--primary)', marginBottom: '1rem', fontSize: '1.4rem' }}>
                        📊 1. Cómo interpretar el Score de IA
                    </h2>
                    <p style={{ color: 'var(--text-muted)', lineHeight: 1.8, marginBottom: '1rem' }}>
                        Nuestro sistema asigna un puntaje de 0 a 100 a cada caballo. Este valor está **calibrado**, lo que
                        significa que un caballo con 30% tiene el doble de probabilidades estadísticas que uno de 15%.
                    </p>
                    <ul style={{ color: 'var(--text-muted)', paddingLeft: '1.5rem', lineHeight: 1.8 }}>
                        <li><strong>Diferencia de Score:</strong> Si el favorito de la IA tiene una ventaja de más de 10 puntos sobre el segundo, se considera una "fija" estadística de alta confianza.</li>
                        <li><strong>Carreras Abiertas:</strong> Cuando los tres primeros caballos tienen scores muy similares (ej. 18%, 17%, 16%), la IA indica que la carrera es altamente competitiva y los factores externos (partida, suerte) cobrarán mayor relevancia.</li>
                    </ul>
                </div>

                <div className="glass-card" style={{ padding: '2rem', marginBottom: '1.5rem' }}>
                    <h2 style={{ color: 'var(--secondary)', marginBottom: '1rem', fontSize: '1.4rem' }}>
                        🏟️ 2. Influencia del Hipódromo y Pista
                    </h2>
                    <p style={{ color: 'var(--text-muted)', lineHeight: 1.8, marginBottom: '1rem' }}>
                        Cada recinto en Chile tiene sus propias "mañas" que el modelo de IA ya considera, pero que tú
                        puedes observar:
                    </p>
                    <ul style={{ color: 'var(--text-muted)', paddingLeft: '1.5rem', lineHeight: 1.8 }}>
                        <li><strong>Hipódromo Chile:</strong> La pista de arena favorece a caballos con resistencia y buena partida frontal. El "peso" de la pista varía según el riego.</li>
                        <li><strong>Club Hípico de Santiago:</strong> El pasto es más sensible al clima. Una lluvia ligera puede transformar a un caballo promedio en un especialista de barro.</li>
                        <li><strong>Posición de Partida:</strong> En distancias cortas (1000m), los cajones interiores suelen tener una ligera ventaja estadística que nuestro modelo integra en su cálculo final.</li>
                    </ul>
                </div>

                <div className="glass-card" style={{ padding: '2rem', marginBottom: '1.5rem' }}>
                    <h2 style={{ color: 'var(--accent)', marginBottom: '1rem', fontSize: '1.4rem' }}>
                        💰 3. Gestión del Presupuesto (Bankroll)
                    </h2>
                    <p style={{ color: 'var(--text-muted)', lineHeight: 1.8, marginBottom: '1rem' }}>
                        El análisis basado en datos requiere disciplina. Ningún sistema, por más avanzado que sea, acierta el 100% de las veces.
                    </p>
                    <ul style={{ color: 'var(--text-muted)', paddingLeft: '1.5rem', lineHeight: 1.8 }}>
                        <li><strong>Unidades fijas:</strong> No apuestes más de una unidad fija por carrera para evitar que una mala racha agote tus fondos.</li>
                        <li><strong>Apuestas Combinadas:</strong> Utiliza el Top 4 de la IA para armar Quinielas y Trifectas, que suelen ofrecer mejores dividendos que la apuesta a Ganador simple.</li>
                        <li><strong>Cabeza Fría:</strong> No intentes recuperar pérdidas apostando impulsivamente en la última carrera del día. Confía en el análisis de largo plazo.</li>
                    </ul>
                </div>

                <div className="glass-card" style={{ padding: '2rem', marginBottom: '1.5rem', borderLeft: '4px solid var(--primary)' }}>
                    <h2 style={{ color: 'var(--primary)', marginBottom: '1rem', fontSize: '1.4rem' }}>
                        🧩 4. La Importancia del Jinete-Preparador
                    </h2>
                    <p style={{ color: 'var(--text-muted)', lineHeight: 1.8 }}>
                        En Pista Inteligente analizamos la **eficiencia histórica** de los binomios. Algunos jinetes tienen
                        un porcentaje de acierto mucho mayor con ciertos preparadores específicos. Si ves un caballo con score alto
                        donde el jinete y preparador tienen una racha ganadora, estás ante una gran oportunidad.
                    </p>
                </div>

                <div style={{ textAlign: 'center', padding: '2rem', background: 'rgba(255,255,255,0.03)', borderRadius: '16px' }}>
                    <h3 style={{ color: 'var(--text-main)', marginBottom: '1rem' }}>¿Quieres poner estos consejos en práctica?</h3>
                    <Link href="/programa" className="cta-button">
                        Ver Predicciones de Hoy
                    </Link>
                </div>
            </article>
        </div>
    )
}
