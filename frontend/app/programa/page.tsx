import { createClient } from '../../utils/supabase/server'
import Link from 'next/link'
import type { Metadata } from 'next'
import BotonQuinela from '@/components/BotonQuinela'
import HipodromoAccordion from '@/components/HipodromoAccordion'


export const metadata: Metadata = {
    title: 'Predicciones Hípica Chilena: Cobertura Nacional Completa con IA',
    description: 'La plataforma líder en pronósticos hípicos con IA. Cobertura total: Hipódromo Chile, Club Hípico de Santiago, Valparaíso Sporting y Club Hípico de Concepción. ¡Obtén tu ventaja competitiva!',
    openGraph: {
        title: 'Predicciones Hípica Chilena: Cobertura Nacional Completa con IA',
        description: 'La plataforma líder en pronósticos hípicos con IA. Cobertura total: Hipódromo Chile, Club Hípico de Santiago, Valparaíso Sporting y Club Hípico de Concepción. ¡Obtén tu ventaja competitiva!',
        type: 'website',
        images: ['/og-image-programa.png'],
    },
    twitter: {
        card: 'summary_large_image',
        title: 'Predicciones Hípica Chilena con IA',
        description: 'Análisis de patrones ganadores en todos los hipódromos de Chile. Score de Confianza exclusivo.',
        images: ['/og-image-programa.png'],
    },
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
        // @ts-ignore
        const hipodromoIds = [...new Set(jornadas.map((j: any) => j.hipodromo_id))]
        const { data: hipodromos } = await supabase
            .from('hipodromos')
            .select('id, nombre')
            .in('id', hipodromoIds)

        // Build hipódromo map with both string and number keys to handle type mismatches
        const hipodromoMap = new Map<string | number, string>()
        for (const h of (hipodromos || [])) {
            // @ts-ignore
            hipodromoMap.set(h.id, h.nombre)
            // @ts-ignore
            hipodromoMap.set(String(h.id), h.nombre)
            // @ts-ignore
            hipodromoMap.set(Number(h.id), h.nombre) // Add explicit Number key just in case
        }

        // Get races for those jornadas
        // @ts-ignore
        const jornadaIds = jornadas.map((j: any) => j.id)
        const { data: carreras } = await supabase
            .from('carreras')
            .select('id, numero, hora, distancia, jornada_id')
            .in('jornada_id', jornadaIds)
            .order('numero', { ascending: true })

            .order('numero', { ascending: true })

        // Check for completed races (those with entries in 'participaciones')
        // We check if there's at least one participation record for the race
        const allCarreraIds = carreras?.map(c => c.id) || []

        // Use a lightweight query to get IDs of races that have results
        // We group by carrera_id to get unique IDs, but since Supabase doesn't support distinct on select easily without rpc
        // we just fetch carrera_id and handle it in JS. Given the page limit (5 jornadas), this is performant enough.
        const { data: results } = await supabase
            .from('participaciones')
            .select('carrera_id')
            .in('carrera_id', allCarreraIds)

        // @ts-ignore
        const completedRaceSet = new Set(results?.map((r: any) => r.carrera_id))

        // Filter only active races (those NOT in completed set)
        const activeCarreras = (carreras || []).filter(c => !completedRaceSet.has(c.id))

        // Get predictions for ACTIVE races only
        const { data: predicciones } = await supabase
            .from('predicciones')
            .select('*')
            .in('carrera_id', activeCarreras.map(c => c.id))
            .order('rank_predicho', { ascending: true })

        // Build response
        const carrerasConPredicciones: Carrera[] = activeCarreras.map((carrera: any) => {
            const jornada = jornadas.find((j: any) => j.id === carrera.jornada_id)
            // Try both number and string keys for hipódromo lookup
            const hipodromoNombre = jornada
                ? (hipodromoMap.get(jornada.hipodromo_id) || hipodromoMap.get(String(jornada.hipodromo_id)))
                : undefined

            const preds = (predicciones || [])
                .filter((p: any) => p.carrera_id === carrera.id)
                .slice(0, 4)
                .map((p: any) => ({
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
        // Filtrar carreras inválidas (carrera 0 o null no existen en la realidad)
        .filter((c: Carrera) => c.carrera && c.carrera > 0)

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

    // Agrupar carreras por hipódromo fuera del JSX para limpieza
    const hipodromoGroups = carreras.reduce((groups, carrera) => {
        const key = carrera.hipodromo
        if (!groups[key]) {
            groups[key] = []
        }
        groups[key].push(carrera)
        return groups
    }, {} as Record<string, typeof carreras>)

    // Ordenar los grupos (opcional, por ejemplo alfabéticamente o por importancia si se tuviera esa data)
    const sortedHipodromos = Object.entries(hipodromoGroups).sort(([a], [b]) => a.localeCompare(b))

    return (
        <>
            {/* SEO Optimized H1 */}
            <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
                <h1 style={{ fontSize: '2rem', color: 'var(--text-main)', marginBottom: '0.5rem', fontWeight: 800 }}>
                    Predicciones Hípica Chilena: Cobertura Nacional Completa con IA
                </h1>
                <p style={{ color: 'var(--text-muted)', fontSize: '1.1rem', maxWidth: '800px', margin: '0 auto' }}>
                    La plataforma líder en pronósticos hípicos ahora integra <strong>todos los hipódromos de Chile</strong>:
                    Hipódromo Chile, Club Hípico de Santiago, Valparaíso Sporting y Club Hípico de Concepción.
                    Analizamos cada carrera con algoritmos de Inteligencia Artificial para detectar patrones ganadores y entregarte
                    predicciones profesionales con un Score de Confianza exclusivo.
                </p>
            </div>

            {/* Stats Summary Cards */}
            <div className="glass-card" style={{ marginBottom: '1.5rem' }}>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '0.75rem', textAlign: 'center' }}>
                    <div style={{ padding: '1rem' }}>
                        <span style={{ fontSize: 'clamp(1.5rem, 4vw, 2.5rem)', color: 'var(--secondary)', display: 'block', fontWeight: 800 }}>
                            {stats.total_carreras}
                        </span>
                        <p style={{ color: 'var(--text-muted)', margin: 0, fontSize: '0.85rem' }}>🏁 Carreras Programadas</p>
                    </div>
                    <div style={{ padding: '1rem' }}>
                        <span style={{ fontSize: 'clamp(1.5rem, 4vw, 2.5rem)', color: 'var(--primary)', display: 'block', fontWeight: 800 }}>
                            {stats.total_caballos}
                        </span>
                        <p style={{ color: 'var(--text-muted)', margin: 0, fontSize: '0.85rem' }}>🏇 Caballos en Competencia</p>
                    </div>
                    <div style={{ padding: '1rem' }}>
                        <span style={{ fontSize: 'clamp(1.5rem, 4vw, 2.5rem)', color: 'var(--accent)', display: 'block', fontWeight: 800 }}>📅</span>
                        <p style={{ color: 'var(--text-main)', margin: 0, fontWeight: 600, fontSize: '0.9rem' }}>{stats.fecha_principal}</p>
                        <p style={{ color: 'var(--text-muted)', margin: 0, fontSize: '0.75rem' }}>Próxima Jornada</p>
                    </div>
                </div>
            </div>

            {/* Section Title */}
            <div className="glass-card">
                <div className="section-title">🔮 Predicciones de Inteligencia Artificial</div>
            </div>

            {/* Predictions - Grouped by Hipódromo with Accordion */}
            <div className="predictions-container">
                {carreras.length > 0 ? (
                    <HipodromoAccordion
                        hipodromos={sortedHipodromos}
                        today={new Date().toLocaleDateString('en-CA', { timeZone: 'America/Santiago' })}
                    />
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
