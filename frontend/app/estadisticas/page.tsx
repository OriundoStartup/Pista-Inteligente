import { createClient } from '../../utils/supabase/server'
import Link from 'next/link'
import type { Metadata } from 'next'

export const metadata: Metadata = {
    title: 'Estadísticas Hípicas Chile 2026 | Base de Datos Completa | Pista Inteligente',
    description: 'Estadísticas completas de carreras de caballos en Chile 2026. Datos de jinetes, caballos, hipódromos y resultados históricos del Hipódromo Chile, Club Hípico y Valparaíso Sporting.',
}

// ISR: Revalidar cada 10 minutos
export const revalidate = 600

async function getEstadisticas() {
    const supabase = await createClient()
    try {
        const { count: totalCarreras } = await supabase
            .from('carreras')
            .select('*', { count: 'exact', head: true })

        const { count: totalCaballos } = await supabase
            .from('caballos')
            .select('*', { count: 'exact', head: true })

        const { count: totalJinetes } = await supabase
            .from('jinetes')
            .select('*', { count: 'exact', head: true })

        const { count: totalJornadas } = await supabase
            .from('jornadas')
            .select('*', { count: 'exact', head: true })

        return {
            total_carreras: totalCarreras || 0,
            total_caballos: totalCaballos || 0,
            total_jinetes: totalJinetes || 0,
            total_jornadas: totalJornadas || 0,
        }
    } catch {
        return {
            total_carreras: 0,
            total_caballos: 0,
            total_jinetes: 0,
            total_jornadas: 0,
        }
    }
}

export default async function EstadisticasPage() {
    const stats = await getEstadisticas()

    return (
        <>
            {/* Header */}
            <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
                <h1 style={{ fontSize: 'clamp(2rem, 5vw, 2.5rem)', color: 'var(--text-main)', marginBottom: '0.5rem', fontWeight: 800 }}>
                    📈 Estadísticas del Sistema
                </h1>
                <p style={{ color: 'var(--text-muted)', fontSize: '1.1rem', maxWidth: '800px', margin: '0 auto', lineHeight: 1.7 }}>
                    Nuestra base de datos contiene información detallada de carreras disputadas en los principales hipódromos de Chile.
                    Estos datos alimentan nuestros modelos de Inteligencia Artificial y se actualizan automáticamente después de cada jornada hípica.
                </p>
            </div>

            {/* Stats Grid */}
            <div className="glass-card" style={{ marginBottom: '2rem' }}>
                <div className="section-title">🗄️ Base de Datos en Números</div>
                <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem', lineHeight: 1.7, fontSize: '0.95rem' }}>
                    Cada cifra que ves a continuación proviene directamente de nuestra base de datos en Supabase. No utilizamos estimaciones:
                    estos son conteos exactos de los registros almacenados. La amplitud de datos es clave para la precisión de nuestros modelos predictivos.
                </p>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem' }}>
                    <div className="glass-card" style={{ textAlign: 'center', padding: '2rem', borderLeft: '4px solid var(--primary)' }}>
                        <span style={{ fontSize: '3rem', color: 'var(--primary)', display: 'block', fontWeight: 800 }}>
                            {stats.total_carreras.toLocaleString()}
                        </span>
                        <p style={{ color: 'var(--text-muted)', margin: '0.5rem 0 0' }}>🏁 Carreras Registradas</p>
                        <p style={{ color: 'var(--text-muted)', margin: 0, fontSize: '0.8rem', lineHeight: 1.5 }}>
                            Cada carrera incluye distancia, tipo de pista, categoría y resultados completos
                        </p>
                    </div>

                    <div className="glass-card" style={{ textAlign: 'center', padding: '2rem', borderLeft: '4px solid var(--secondary)' }}>
                        <span style={{ fontSize: '3rem', color: 'var(--secondary)', display: 'block', fontWeight: 800 }}>
                            {stats.total_caballos.toLocaleString()}
                        </span>
                        <p style={{ color: 'var(--text-muted)', margin: '0.5rem 0 0' }}>🐴 Caballos</p>
                        <p style={{ color: 'var(--text-muted)', margin: 0, fontSize: '0.8rem', lineHeight: 1.5 }}>
                            Perfil individual con historial de rendimiento, preparador y haras de origen
                        </p>
                    </div>

                    <div className="glass-card" style={{ textAlign: 'center', padding: '2rem', borderLeft: '4px solid var(--accent)' }}>
                        <span style={{ fontSize: '3rem', color: 'var(--accent)', display: 'block', fontWeight: 800 }}>
                            {stats.total_jinetes.toLocaleString()}
                        </span>
                        <p style={{ color: 'var(--text-muted)', margin: '0.5rem 0 0' }}>🏇 Jinetes</p>
                        <p style={{ color: 'var(--text-muted)', margin: 0, fontSize: '0.8rem', lineHeight: 1.5 }}>
                            Estadísticas de victorias, eficiencia y combinaciones jinete-caballo exitosas
                        </p>
                    </div>

                    <div className="glass-card" style={{ textAlign: 'center', padding: '2rem', borderLeft: '4px solid #FFD700' }}>
                        <span style={{ fontSize: '3rem', color: '#FFD700', display: 'block', fontWeight: 800 }}>
                            {stats.total_jornadas.toLocaleString()}
                        </span>
                        <p style={{ color: 'var(--text-muted)', margin: '0.5rem 0 0' }}>📅 Jornadas</p>
                        <p style={{ color: 'var(--text-muted)', margin: 0, fontSize: '0.8rem', lineHeight: 1.5 }}>
                            Días de carrera procesados, cada uno con múltiples carreras analizadas
                        </p>
                    </div>
                </div>
            </div>

            {/* Performance CTA */}
            <div className="glass-card" style={{
                marginBottom: '2rem',
                padding: 'clamp(1.25rem, 4vw, 2rem)',
                background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(52, 211, 153, 0.05))',
                textAlign: 'center'
            }}>
                <div style={{
                    fontSize: 'clamp(1.5rem, 4vw, 2rem)',
                    marginBottom: 'clamp(0.75rem, 2vw, 1rem)'
                }}>📊</div>
                <h3 style={{
                    color: 'var(--text-main)',
                    marginBottom: 'clamp(0.5rem, 2vw, 0.75rem)',
                    fontSize: 'clamp(1.1rem, 3.5vw, 1.5rem)',
                    fontWeight: 700,
                    lineHeight: 1.3
                }}>
                    ¿Quieres ver el rendimiento de nuestras predicciones?
                </h3>
                <p style={{
                    color: 'var(--text-muted)',
                    fontSize: 'clamp(0.9rem, 2.5vw, 1rem)',
                    lineHeight: 1.5,
                    maxWidth: '600px',
                    margin: '0 auto clamp(1rem, 3vw, 1.5rem) auto'
                }}>
                    Conoce la precisión real de Pista Inteligente con datos verificables. Comparamos cada predicción
                    con los resultados oficiales para mostrarte tasas reales de acierto.
                </p>
                <Link
                    href="/precision"
                    className="cta-button"
                    style={{ display: 'inline-block' }}
                >
                    Ver Rendimiento Detallado
                </Link>
            </div>

            {/* Hipódromos - Enriched with original content */}
            <div className="glass-card" style={{ marginBottom: '2rem' }}>
                <div className="section-title">🏟️ Hipódromos Cubiertos</div>
                <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem', lineHeight: 1.7, fontSize: '0.95rem' }}>
                    Chile tiene una tradición hípica que se remonta a mediados del siglo XIX. Los cuatro principales recintos
                    del país ofrecen carreras regulares durante todo el año, cada uno con características únicas en cuanto a
                    superficie de pista, distancias disponibles y nivel de competencia.
                </p>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
                    <div className="glass-card" style={{ padding: '1.5rem' }}>
                        <h3 style={{ color: 'var(--primary)', marginBottom: '0.75rem', fontSize: '1.25rem' }}>🏇 Hipódromo Chile</h3>
                        <p style={{ color: 'var(--text-muted)', margin: 0, lineHeight: 1.7, fontSize: '0.95rem' }}>
                            Santiago (Independencia) — El hipódromo con mayor actividad del país. Ofrece jornadas de lunes a viernes
                            durante todo el año. Su pista de arena de 1.500 metros permite carreras desde los 800 hasta los 2.400 metros,
                            con un calendario que incluye tanto carreras de categorías iniciales como clásicos importantes.
                            Es el principal recinto del turf nacional y el que más datos aporta a nuestro modelo.
                        </p>
                    </div>

                    <div className="glass-card" style={{ padding: '1.5rem' }}>
                        <h3 style={{ color: 'var(--secondary)', marginBottom: '0.75rem', fontSize: '1.25rem' }}>🏛️ Club Hípico de Santiago</h3>
                        <p style={{ color: 'var(--text-muted)', margin: 0, lineHeight: 1.7, fontSize: '0.95rem' }}>
                            Santiago (Blanco Encalada) — Fundado en 1869, es el recinto hípico más antiguo de Chile y uno de los más
                            prestigiosos de Sudamérica. Su pista de pasto de 2.000 metros alberga los clásicos más importantes del
                            calendario hípico nacional, incluyendo el St. Leger y el Gran Premio Nacional. Las carreras en pasto
                            requieren un análisis diferenciado, ya que la superficie afecta significativamente el rendimiento.
                        </p>
                    </div>

                    <div className="glass-card" style={{ padding: '1.5rem' }}>
                        <h3 style={{ color: '#10b981', marginBottom: '0.75rem', fontSize: '1.25rem' }}>🌊 Valparaíso Sporting</h3>
                        <p style={{ color: 'var(--text-muted)', margin: 0, lineHeight: 1.7, fontSize: '0.95rem' }}>
                            Viña del Mar — Conocido como la cuna de la hípica chilena, este recinto costero en Viña del Mar
                            es sede del legendario Derby, una de las carreras clásicas más importantes de Sudamérica. Su pista
                            de pasto ofrece un recorrido técnico con curvas que favorecen a caballos con buen manejo táctico.
                            Las condiciones climáticas costeras son un factor que nuestro modelo incorpora en el análisis.
                        </p>
                    </div>

                    <div className="glass-card" style={{ padding: '1.5rem' }}>
                        <h3 style={{ color: '#f59e0b', marginBottom: '0.75rem', fontSize: '1.25rem' }}>🌲 Club Hípico de Concepción</h3>
                        <p style={{ color: 'var(--text-muted)', margin: 0, lineHeight: 1.7, fontSize: '0.95rem' }}>
                            Hualpén (Biobío) — Principal recinto hípico del sur de Chile. Ofrece jornadas regulares con carreras
                            especiales para la zona sur del país. Aunque tiene menos actividad que los recintos de Santiago,
                            su inclusión en nuestro análisis permite una cobertura nacional completa y detectar jinetes o caballos
                            que compiten en múltiples hipódromos.
                        </p>
                    </div>
                </div>
            </div>

            {/* Model Info - Expanded with context */}
            <div className="glass-card" style={{ marginBottom: '2rem' }}>
                <div className="section-title">🤖 Tecnología Utilizada</div>
                <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem', lineHeight: 1.7, fontSize: '0.95rem' }}>
                    Nuestro sistema predictivo utiliza un <strong>ensemble de tres modelos de Gradient Boosting</strong>,
                    una arquitectura que combina las fortalezas de cada modelo para lograr predicciones más robustas.
                    Cada modelo procesa las mismas variables de entrada pero con diferentes enfoques de optimización,
                    y un meta-learner combina sus salidas en una predicción final calibrada.
                </p>

                <table className="modern-table">
                    <thead>
                        <tr>
                            <th>Componente</th>
                            <th>Tecnología</th>
                            <th>Descripción</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Modelo Principal</td>
                            <td style={{ color: 'var(--primary)', fontWeight: 600 }}>LightGBM</td>
                            <td>Gradient Boosting optimizado para ranking. Excelente velocidad de entrenamiento y manejo de datos categóricos.</td>
                        </tr>
                        <tr>
                            <td>Modelo Secundario</td>
                            <td style={{ color: 'var(--secondary)', fontWeight: 600 }}>XGBoost</td>
                            <td>Gradient Boosting con regularización avanzada. Aporta robustez al ensemble y reduce sobreajuste.</td>
                        </tr>
                        <tr>
                            <td>Modelo Terciario</td>
                            <td style={{ color: 'var(--accent)', fontWeight: 600 }}>CatBoost</td>
                            <td>Especializado en variables categóricas (jinete, preparador, haras). Maneja naturalmente datos con alta cardinalidad.</td>
                        </tr>
                        <tr>
                            <td>Meta-Learner</td>
                            <td style={{ color: '#FFD700', fontWeight: 600 }}>Ridge Regression</td>
                            <td>Combina las predicciones de los 3 modelos base, ponderando la contribución de cada uno según su rendimiento histórico.</td>
                        </tr>
                        <tr>
                            <td>Calibración</td>
                            <td style={{ color: 'var(--primary)', fontWeight: 600 }}>Isotonic Regression</td>
                            <td>Ajusta las probabilidades finales para que reflejen la frecuencia real de aciertos observada.</td>
                        </tr>
                    </tbody>
                </table>

                <p style={{ color: 'var(--text-muted)', marginTop: '1.5rem', lineHeight: 1.7, fontSize: '0.95rem' }}>
                    Si deseas conocer más detalles sobre nuestra metodología, visita la{' '}
                    <Link href="/metodologia" style={{ color: 'var(--primary)', textDecoration: 'underline' }}>página de Metodología</Link>,
                    donde explicamos en profundidad el pipeline de datos, las features utilizadas y el proceso de validación.
                </p>
            </div>
        </>
    )
}
