import { createClient } from '@/utils/supabase/server'
import Link from 'next/link'
import type { Metadata } from 'next'
import BotonQuinela from '@/components/BotonQuinela'

export const metadata: Metadata = {
    title: 'Predicciones Hipódromo Chile | Pista Inteligente',
    description: 'Programa completo y predicciones con IA para Hipódromo Chile y Club Hípico de Chile. Pronósticos profesionales y análisis en tiempo real.',
}

// ISR: Revalidar cada 5 minutos para datos frescos
export const revalidate = 300

// Types
interface Prediccion {
    numero: number
    caballo: string
    jinete: string
    puntaje_ia: number
}

interface Carrera {
    id: string
    hipodromo: string
    carrera: number
    fecha: string
    hora: string
    distancia: number
    predicciones: Prediccion[]
}

// Fetch predictions from Supabase
async function getPredicciones(): Promise<{ carreras: Carrera[], stats: { total_carreras: number, total_caballos: number, fecha_principal: string } }> {
    const supabase = await createClient()
    try {
        // Get upcoming jornadas (Force Chile Timezone)
        const today = new Date().toLocaleDateString('en-CA', { timeZone: 'America/Santiago' })
        const { data: jornadas } = await supabase
            .from('jornadas')
            .select('id, fecha, hipodromo_id')
            .gte('fecha', today)
            .order('fecha', { ascending: true })
            .limit(5)

        if (!jornadas || jornadas.length === 0) {
            return {
                carreras: [],
                stats: { total_carreras: 0, total_caballos: 0, fecha_principal: today }
            }
        }

        // Get hipodromos names
        const hipodromoIds = [...new Set(jornadas.map(j => j.hipodromo_id))]
        const { data: hipodromos } = await supabase
            .from('hipodromos')
            .select('id, nombre')
            .in('id', hipodromoIds)

        // Build hipódromo map with both string and number keys to handle type mismatches
        const hipodromoMap = new Map<string | number, string>()
        for (const h of (hipodromos || [])) {
            hipodromoMap.set(h.id, h.nombre)
            hipodromoMap.set(String(h.id), h.nombre)
        }

        // Get races for those jornadas
        const jornadaIds = jornadas.map(j => j.id)
        const { data: carreras } = await supabase
            .from('carreras')
            .select('id, numero, hora, distancia, jornada_id')
            .in('jornada_id', jornadaIds)
            .order('numero', { ascending: true })

        // Get predictions
        const { data: predicciones } = await supabase
            .from('predicciones')
            .select('*')
            .in('carrera_id', carreras?.map(c => c.id) || [])
            .order('rank_predicho', { ascending: true })

        // Build response
        const carrerasConPredicciones: Carrera[] = (carreras || []).map(carrera => {
            const jornada = jornadas.find(j => j.id === carrera.jornada_id)
            // Try both number and string keys for hipódromo lookup
            const hipodromoNombre = jornada
                ? (hipodromoMap.get(jornada.hipodromo_id) || hipodromoMap.get(String(jornada.hipodromo_id)))
                : undefined

            const preds = (predicciones || [])
                .filter(p => p.carrera_id === carrera.id)
                .slice(0, 4)
                .map(p => ({
                    numero: p.numero_caballo || 0,
                    caballo: p.caballo || 'N/A',
                    jinete: p.jinete || 'N/A',
                    puntaje_ia: p.probabilidad ? (p.probabilidad * 100) : 50
                }))

            return {
                id: carrera.id,
                hipodromo: hipodromoNombre || 'Hipódromo Chile',
                carrera: carrera.numero,
                fecha: jornada?.fecha || today,
                hora: carrera.hora || '00:00',
                distancia: carrera.distancia || 1000,
                predicciones: preds.length > 0 ? preds : [
                    { numero: 1, caballo: 'Datos pendientes', jinete: '-', puntaje_ia: 0 }
                ]
            }
        })

        return {
            carreras: carrerasConPredicciones,
            stats: {
                total_carreras: carrerasConPredicciones.length,
                total_caballos: carrerasConPredicciones.reduce((sum, c) => sum + c.predicciones.length, 0),
                fecha_principal: jornadas[0]?.fecha || today
            }
        }
    } catch (error) {
        console.error('Error fetching predictions:', error)
        return {
            carreras: [],
            stats: { total_carreras: 0, total_caballos: 0, fecha_principal: new Date().toISOString().split('T')[0] }
        }
    }
}

export default async function ProgramaPage() {
    const { carreras, stats } = await getPredicciones()

    return (
        <>
            {/* SEO Optimized H1 */}
            <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
                <h1 style={{ fontSize: '2rem', color: 'var(--text-main)', marginBottom: '0.5rem', fontWeight: 800 }}>
                    Predicciones para Hipódromo Chile y Club Hípico con Inteligencia Artificial
                </h1>
                <p style={{ color: 'var(--text-muted)', fontSize: '1.1rem', maxWidth: '800px', margin: '0 auto' }}>
                    Utilizamos modelos de aprendizaje automático de última generación para analizar cada carrera del
                    <strong> Programa Hipódromo Chile</strong> y del <strong>Club Hípico</strong>.
                    Nuestros algoritmos detectan patrones ocultos en miles de datos históricos para entregarte pronósticos
                    profesionales con un Score de Confianza único en el mercado.
                </p>
            </div>

            {/* Stats Summary Cards */}
            <div className="glass-card" style={{ marginBottom: '1.5rem' }}>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem', textAlign: 'center' }}>
                    <div style={{ padding: '1.5rem' }}>
                        <span style={{ fontSize: '2.5rem', color: 'var(--secondary)', display: 'block', fontWeight: 800 }}>
                            {stats.total_carreras}
                        </span>
                        <p style={{ color: 'var(--text-muted)', margin: 0 }}>🏁 Carreras Programadas</p>
                    </div>
                    <div style={{ padding: '1.5rem' }}>
                        <span style={{ fontSize: '2.5rem', color: 'var(--primary)', display: 'block', fontWeight: 800 }}>
                            {stats.total_caballos}
                        </span>
                        <p style={{ color: 'var(--text-muted)', margin: 0 }}>🏇 Caballos en Competencia</p>
                    </div>
                    <div style={{ padding: '1.5rem' }}>
                        <span style={{ fontSize: '2.5rem', color: 'var(--accent)', display: 'block', fontWeight: 800 }}>📅</span>
                        <p style={{ color: 'var(--text-main)', margin: 0, fontWeight: 600 }}>{stats.fecha_principal}</p>
                        <p style={{ color: 'var(--text-muted)', margin: 0, fontSize: '0.85rem' }}>Próxima Jornada</p>
                    </div>
                </div>
            </div>

            {/* Section Title */}
            <div className="glass-card">
                <div className="section-title">🔮 Predicciones de Inteligencia Artificial</div>
            </div>

            {/* Predictions - Grouped by Hipódromo */}
            <div className="predictions-container">
                {carreras.length > 0 ? (
                    // Agrupar carreras por hipódromo
                    (() => {
                        const hipodromoGroups = carreras.reduce((groups, carrera) => {
                            const key = carrera.hipodromo
                            if (!groups[key]) {
                                groups[key] = []
                            }
                            groups[key].push(carrera)
                            return groups
                        }, {} as Record<string, typeof carreras>)

                        return Object.entries(hipodromoGroups).map(([hipodromo, carrerasHip]) => (
                            <div key={hipodromo} className="glass-card" style={{ marginBottom: '2rem', padding: '1.5rem' }}>
                                {/* Header del Hipódromo */}
                                <div style={{
                                    borderBottom: '2px solid var(--primary)',
                                    marginBottom: '1.5rem',
                                    paddingBottom: '1rem'
                                }}>
                                    <h2 style={{
                                        color: 'var(--primary)',
                                        fontSize: '1.5rem',
                                        fontWeight: 800,
                                        margin: 0,
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '0.5rem'
                                    }}>
                                        🏇 {hipodromo}
                                        <span style={{
                                            fontSize: '0.9rem',
                                            color: 'var(--text-muted)',
                                            fontWeight: 400
                                        }}>
                                            ({carrerasHip.length} carreras)
                                        </span>
                                    </h2>
                                    <p style={{ color: 'var(--text-muted)', margin: '0.5rem 0 0 0', fontSize: '0.9rem' }}>
                                        📅 {carrerasHip[0]?.fecha}
                                    </p>
                                </div>

                                {/* Carreras de este hipódromo */}
                                {carrerasHip.sort((a, b) => a.carrera - b.carrera).map((carrera) => (
                                    <div key={carrera.id} style={{
                                        marginBottom: '1.5rem',
                                        padding: '1rem',
                                        background: 'rgba(255,255,255,0.03)',
                                        borderRadius: '8px',
                                        borderLeft: '3px solid var(--secondary)'
                                    }}>
                                        <h3 style={{ color: 'white', marginBottom: '0.75rem', fontSize: '1.1rem' }}>
                                            Carrera {carrera.carrera}
                                            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginLeft: '1rem' }}>
                                                🕒 {carrera.hora} | 🏁 {carrera.distancia}m
                                            </span>
                                        </h3>

                                        <table className="modern-table">
                                            <thead>
                                                <tr>
                                                    <th>#</th>
                                                    <th>Caballo</th>
                                                    <th>Jinete</th>
                                                    <th>IA Score</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {carrera.predicciones.map((pred, index) => (
                                                    <tr key={index}>
                                                        <td>{pred.numero}</td>
                                                        <td style={{ fontWeight: 600, color: 'var(--text-main)' }}>{pred.caballo}</td>
                                                        <td>{pred.jinete}</td>
                                                        <td>
                                                            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                                                {index === 0 && <span title="Favorito de la IA" style={{ fontSize: '1.2rem' }}>🥇</span>}
                                                                {index === 1 && <span title="Segunda Opción" style={{ fontSize: '1rem', opacity: 0.8 }}>🥈</span>}
                                                                {index === 2 && <span title="Tercera Opción" style={{ fontSize: '1rem', opacity: 0.8 }}>🥉</span>}
                                                                <div style={{ flexGrow: 1, minWidth: '80px' }}>
                                                                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '2px' }}>
                                                                        <span style={{ fontWeight: 'bold', color: 'white' }}>IA Confianza</span>
                                                                        <span style={{ fontWeight: 'bold', color: pred.puntaje_ia > 80 ? '#4ade80' : pred.puntaje_ia > 50 ? '#fbbf24' : '#f87171' }}>
                                                                            {pred.puntaje_ia.toFixed(1)}%
                                                                        </span>
                                                                    </div>
                                                                    <div style={{ background: 'rgba(255,255,255,0.1)', height: '6px', borderRadius: '10px', overflow: 'hidden' }}>
                                                                        <div
                                                                            style={{
                                                                                width: `${pred.puntaje_ia}%`,
                                                                                height: '100%',
                                                                                background: pred.puntaje_ia > 80 ? '#4ade80' : pred.puntaje_ia > 50 ? '#fbbf24' : '#f87171',
                                                                                borderRadius: '10px'
                                                                            }}
                                                                        />
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        </td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                ))}
                            </div>
                        ))
                    })()
                ) : (
                    <div className="glass-card" style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
                        <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>🏇</div>
                        <h2 style={{ color: 'var(--text-main)', marginBottom: '1rem' }}>No hay carreras programadas</h2>
                        <p style={{ marginBottom: '1.5rem', maxWidth: '400px', margin: '0 auto 1.5rem' }}>
                            Actualmente no hay carreras disponibles. Las predicciones se actualizan diariamente cuando hay jornadas programadas.
                        </p>
                        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
                            <Link href="/" className="cta-button">Volver al Inicio</Link>
                            <Link href="/estadisticas" className="nav-link" style={{ padding: '1rem 2rem', border: '1px solid var(--primary)', borderRadius: '50px' }}>
                                Ver Estadísticas
                            </Link>
                        </div>
                    </div>
                )}
            </div>

            {/* Sección de Agradecimiento - Momento perfecto después de ver predicciones */}
            {carreras.length > 0 && (
                <div
                    className="glass-card"
                    style={{
                        marginTop: '2rem',
                        textAlign: 'center',
                        padding: '2rem',
                        background: 'linear-gradient(135deg, rgba(22, 163, 74, 0.15), rgba(6, 182, 212, 0.1))',
                        borderTop: '3px solid rgba(22, 163, 74, 0.5)'
                    }}
                >
                    <h3 style={{ color: 'var(--text-main)', marginBottom: '0.75rem', fontSize: '1.25rem' }}>
                        🍀 ¿Te ayudaron nuestras predicciones?
                    </h3>
                    <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem', maxWidth: '500px', margin: '0 auto 1.5rem' }}>
                        Si nuestros datos te fueron útiles, considera apoyarnos para mantener el servidor corriendo y mejorar nuestro modelo de IA.
                    </p>
                    <BotonQuinela linkPago="https://link.mercadopago.cl/pistainteligente" />
                </div>
            )}
        </>
    )
}
