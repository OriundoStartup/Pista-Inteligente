import Link from 'next/link'
import type { Metadata } from 'next'
import { createClient } from '@supabase/supabase-js'
import BotonQuinela from '@/components/BotonQuinela'
import { AdBannerHorizontal } from '@/components/AdSense'

export const metadata: Metadata = {
    title: 'Rendimiento Pista Inteligente - Precisión Real | Predicciones Hípicas IA',
    description: 'Transparencia total: Conoce el rendimiento real de Pista Inteligente. Ganador exacto, Quiniela, Trifecta y Superfecta por hipódromo.',
}

export const revalidate = 300 // Cache 5 minutos — los datos se actualizan con cada sync

interface StatsData {
    total_carreras: number
    ganador_pct: number
    quiniela_pct: number
    trifecta_pct: number
    superfecta_pct: number
    ganador_count: number
    quiniela_count: number
    trifecta_count: number
    superfecta_count: number
}

interface RaceResult {
    fecha: string
    hipodromo: string
    nro_carrera: number
    acierto_ganador: boolean
    acierto_quiniela: boolean
    acierto_trifecta: boolean
    acierto_superfecta: boolean
    prediccion_top4: string[]
    resultado_top4: string[]
}

interface PerformanceData {
    generated_at: string
    global: {
        last_30_days: StatsData
        last_90_days: StatsData
        all_time: StatsData
    }
    by_hipodromo: { [key: string]: StatsData }
    recent_races: RaceResult[]
}

async function getPerformanceData(): Promise<PerformanceData | null> {
    try {
        const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
        const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

        if (!supabaseUrl || !supabaseKey) {
            console.error('Supabase credentials not configured')
            return null
        }

        const supabase = createClient(supabaseUrl, supabaseKey)

        // Fetch global stats
        const { data: statsRow, error: statsError } = await supabase
            .from('rendimiento_stats')
            .select('data')
            .eq('id', 'global_stats')
            .single()

        if (statsError || !statsRow) {
            console.error('Error fetching stats:', statsError)
            return null
        }

        const statsData = typeof statsRow.data === 'string'
            ? JSON.parse(statsRow.data)
            : statsRow.data

        // Fetch races with at least one successful prediction
        // Using or() filter to get races where ANY prediction type succeeded
        const { data: recentRaces, error: racesError } = await supabase
            .from('rendimiento_historico')
            .select('*')
            .gte('fecha', '2025-11-01') // Include all historical data since system launch
            .or('acierto_ganador.eq.true,acierto_quiniela.eq.true,acierto_trifecta.eq.true,acierto_superfecta.eq.true')
            .order('fecha', { ascending: false })
            .limit(150) // Limit for performance — shows ~1 month of data

        // Filter, validate, and deduplicate race results
        const races: RaceResult[] = (recentRaces || [])
            .filter((r: any) => {
                // Validate essential data
                if (!r.fecha || !r.hipodromo || !r.nro_carrera) return false
                if (r.nro_carrera <= 0) return false // Filter invalid race numbers
                return true
            })
            .reduce((acc: RaceResult[], r: any) => {
                // Deduplication: avoid duplicates by fecha-hipodromo-carrera
                const key = `${r.fecha}-${r.hipodromo}-${r.nro_carrera}`
                const isDuplicate = acc.find((existing) =>
                    `${existing.fecha}-${existing.hipodromo}-${existing.nro_carrera}` === key
                )

                if (!isDuplicate) {
                    acc.push({
                        fecha: r.fecha,
                        hipodromo: r.hipodromo,
                        nro_carrera: r.nro_carrera,
                        acierto_ganador: r.acierto_ganador,
                        acierto_quiniela: r.acierto_quiniela,
                        acierto_trifecta: r.acierto_trifecta,
                        acierto_superfecta: r.acierto_superfecta,
                        prediccion_top4: typeof r.prediccion_top4 === 'string'
                            ? JSON.parse(r.prediccion_top4)
                            : r.prediccion_top4 || [],
                        resultado_top4: typeof r.resultado_top4 === 'string'
                            ? JSON.parse(r.resultado_top4)
                            : r.resultado_top4 || []
                    })
                }
                return acc
            }, [])

        return {
            generated_at: statsData.updated_at || new Date().toISOString(),
            global: {
                last_30_days: statsData.last_30_days || { total_carreras: 0, ganador_pct: 0, quiniela_pct: 0, trifecta_pct: 0, superfecta_pct: 0, ganador_count: 0, quiniela_count: 0, trifecta_count: 0, superfecta_count: 0 },
                last_90_days: statsData.last_90_days || { total_carreras: 0, ganador_pct: 0, quiniela_pct: 0, trifecta_pct: 0, superfecta_pct: 0, ganador_count: 0, quiniela_count: 0, trifecta_count: 0, superfecta_count: 0 },
                all_time: statsData.all_time || { total_carreras: 0, ganador_pct: 0, quiniela_pct: 0, trifecta_pct: 0, superfecta_pct: 0, ganador_count: 0, quiniela_count: 0, trifecta_count: 0, superfecta_count: 0 }
            },
            by_hipodromo: statsData.by_hipodromo || {},
            recent_races: races
        }
    } catch (error) {
        console.error('Error loading performance data:', error)
        return null
    }
}


function StatCard({ label, value, count, total, color }: {
    label: string, value: number, count?: number, total?: number, color: string
}) {
    return (
        <div className="glass-card stat-card" style={{
            textAlign: 'center',
            padding: '1.5rem',
            borderLeft: `4px solid ${color}`
        }}>
            <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>{label}</div>
            <div style={{ fontSize: '2.5rem', fontWeight: 800, color: color, marginBottom: '0.25rem' }}>
                {value}%
            </div>
            {count !== undefined && total !== undefined && (
                <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                    {count} de {total}
                </div>
            )}
        </div>
    )
}

function HipodromoCard({ name, stats }: { name: string, stats: StatsData }) {
    const getIcon = (hip: string) => {
        if (hip.includes('Chile')) return '🏇'
        if (hip.includes('Club')) return '🏛️'
        if (hip.includes('Valparaíso')) return '🌊'
        if (hip.includes('Concepción')) return '🌲'
        return '🏇'
    }

    return (
        <div className="glass-card hipodromo-card" style={{ padding: '1.5rem', marginBottom: '1rem' }}>
            <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                marginBottom: '1rem',
                borderBottom: '1px solid rgba(255,255,255,0.1)',
                paddingBottom: '0.75rem'
            }}>
                <span style={{ fontSize: '1.5rem' }}>{getIcon(name)}</span>
                <h3 style={{ margin: 0, color: 'var(--text-main)', fontSize: '1.1rem' }}>{name}</h3>
                <span className="badge" style={{
                    marginLeft: 'auto',
                    background: 'rgba(99, 102, 241, 0.2)',
                    color: 'var(--primary)',
                    padding: '0.25rem 0.75rem',
                    borderRadius: '20px',
                    fontSize: '0.8rem'
                }}>
                    {stats.total_carreras} carreras
                </span>
            </div>

            <div className="stats-grid" style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(4, 1fr)',
                gap: '0.75rem',
                textAlign: 'center'
            }}>
                <div className="stat-mini">
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>🥇 Ganador</div>
                    <div style={{ fontSize: '1.3rem', fontWeight: 700, color: '#FFD700' }}>{stats.ganador_pct}%</div>
                </div>
                <div className="stat-mini">
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>🎯 Quiniela</div>
                    <div style={{ fontSize: '1.3rem', fontWeight: 700, color: '#C0C0C0' }}>{stats.quiniela_pct}%</div>
                </div>
                <div className="stat-mini">
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>🏆 Trifecta</div>
                    <div style={{ fontSize: '1.3rem', fontWeight: 700, color: '#CD7F32' }}>{stats.trifecta_pct}%</div>
                </div>
                <div className="stat-mini">
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>⭐ Superfecta</div>
                    <div style={{ fontSize: '1.3rem', fontWeight: 700, color: 'var(--primary)' }}>{stats.superfecta_pct}%</div>
                </div>
            </div>
        </div>
    )
}


function RaceResultCard({ race }: { race: RaceResult }) {
    const formatDate = (fecha: string) => {
        const d = new Date(fecha + 'T12:00:00')
        return d.toLocaleDateString('es-CL', { day: '2-digit', month: 'short', year: 'numeric' })
    }

    const getIcon = (hip: string) => {
        if (hip.includes('Chile')) return '🏇'
        if (hip.includes('Club')) return '🏛️'
        if (hip.includes('Valparaíso')) return '🌊'
        if (hip.includes('Concepción')) return '🌲'
        return '🏇'
    }

    // Determine the best match type for border and badge
    const getBestMatch = () => {
        if (race.acierto_superfecta) return { color: 'var(--primary)', label: '⭐ SUPERFECTA', bg: 'rgba(99, 102, 241, 0.1)', border: 'rgba(99, 102, 241, 0.3)' }
        if (race.acierto_trifecta) return { color: '#CD7F32', label: '🏆 TRIFECTA', bg: 'rgba(205, 127, 50, 0.1)', border: 'rgba(205, 127, 50, 0.3)' }
        if (race.acierto_quiniela) return { color: '#C0C0C0', label: '🎯 QUINIELA', bg: 'rgba(192, 192, 192, 0.1)', border: 'rgba(192, 192, 192, 0.3)' }
        if (race.acierto_ganador) return { color: '#FFD700', label: '🥇 GANADOR', bg: 'rgba(255, 215, 0, 0.1)', border: 'rgba(255, 215, 0, 0.2)' }
        return null
    }
    const bestMatch = getBestMatch()

    return (
        <div className="glass-card race-card" style={{
            padding: '1.25rem',
            marginBottom: '1rem',
            borderLeft: bestMatch ? `4px solid ${bestMatch.color}` : '4px solid transparent',
            background: 'rgba(255, 255, 255, 0.03)'
        }}>
            {/* Header */}
            <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '1rem',
                borderBottom: '1px solid rgba(255,255,255,0.05)',
                paddingBottom: '0.75rem'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span style={{ fontSize: '1.2rem' }}>{getIcon(race.hipodromo)}</span>
                    <div>
                        <div style={{ fontWeight: 700, fontSize: '0.95rem', color: 'var(--text-main)' }}>
                            {race.hipodromo}
                        </div>
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                            {formatDate(race.fecha)} • Carrera {race.nro_carrera}
                        </div>
                    </div>
                </div>
                <div style={{ display: 'flex', gap: '0.35rem', flexWrap: 'wrap', justifyContent: 'flex-end' }}>
                    {race.acierto_ganador && (
                        <span style={{ background: 'rgba(255, 215, 0, 0.1)', color: '#FFD700', padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.7rem', border: '1px solid rgba(255, 215, 0, 0.2)', fontWeight: 600 }}>🥇</span>
                    )}
                    {race.acierto_quiniela && (
                        <span style={{ background: 'rgba(192, 192, 192, 0.1)', color: '#C0C0C0', padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.7rem', border: '1px solid rgba(192, 192, 192, 0.2)', fontWeight: 600 }}>🎯</span>
                    )}
                    {race.acierto_trifecta && (
                        <span style={{ background: 'rgba(205, 127, 50, 0.1)', color: '#CD7F32', padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.7rem', border: '1px solid rgba(205, 127, 50, 0.2)', fontWeight: 600 }}>🏆</span>
                    )}
                    {race.acierto_superfecta && (
                        <span style={{ background: 'rgba(99, 102, 241, 0.1)', color: 'var(--primary)', padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.7rem', border: '1px solid rgba(99, 102, 241, 0.2)', fontWeight: 600 }}>⭐</span>
                    )}
                </div>
            </div>

            {/* Hits Grid */}
            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(4, 1fr)',
                gap: '0.5rem',
                marginBottom: '1rem',
                textAlign: 'center'
            }}>
                <div className={`hit-box ${race.acierto_ganador ? 'hit' : ''}`} style={{
                    padding: '0.5rem',
                    borderRadius: '8px',
                    background: race.acierto_ganador ? 'rgba(255, 215, 0, 0.1)' : 'rgba(255,255,255,0.02)',
                    border: race.acierto_ganador ? '1px solid rgba(255, 215, 0, 0.3)' : '1px solid rgba(255,255,255,0.05)'
                }}>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '0.2rem' }}>Ganador</div>
                    <div style={{ fontSize: '1.1rem' }}>{race.acierto_ganador ? '✅' : '❌'}</div>
                </div>
                <div className={`hit-box ${race.acierto_quiniela ? 'hit' : ''}`} style={{
                    padding: '0.5rem',
                    borderRadius: '8px',
                    background: race.acierto_quiniela ? 'rgba(192, 192, 192, 0.1)' : 'rgba(255,255,255,0.02)',
                    border: race.acierto_quiniela ? '1px solid rgba(192, 192, 192, 0.3)' : '1px solid rgba(255,255,255,0.05)'
                }}>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '0.2rem' }}>Quiniela</div>
                    <div style={{ fontSize: '1.1rem' }}>{race.acierto_quiniela ? '✅' : '❌'}</div>
                </div>
                <div className={`hit-box ${race.acierto_trifecta ? 'hit' : ''}`} style={{
                    padding: '0.5rem',
                    borderRadius: '8px',
                    background: race.acierto_trifecta ? 'rgba(205, 127, 50, 0.1)' : 'rgba(255,255,255,0.02)',
                    border: race.acierto_trifecta ? '1px solid rgba(205, 127, 50, 0.3)' : '1px solid rgba(255,255,255,0.05)'
                }}>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '0.2rem' }}>Trifecta</div>
                    <div style={{ fontSize: '1.1rem' }}>{race.acierto_trifecta ? '✅' : '❌'}</div>
                </div>
                <div className={`hit-box ${race.acierto_superfecta ? 'hit' : ''}`} style={{
                    padding: '0.5rem',
                    borderRadius: '8px',
                    background: race.acierto_superfecta ? 'rgba(99, 102, 241, 0.1)' : 'rgba(255,255,255,0.02)',
                    border: race.acierto_superfecta ? '1px solid rgba(99, 102, 241, 0.3)' : '1px solid rgba(255,255,255,0.05)'
                }}>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '0.2rem' }}>Super</div>
                    <div style={{ fontSize: '1.1rem' }}>{race.acierto_superfecta ? '✅' : '❌'}</div>
                </div>
            </div>

            {/* Comparison Details */}
            <div style={{
                background: 'rgba(0,0,0,0.2)',
                borderRadius: '8px',
                padding: '0.75rem',
                fontSize: '0.85rem'
            }}>
                <div className="comparison-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                    <div>
                        <div style={{ color: 'var(--primary)', marginBottom: '0.5rem', fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: 600 }}>
                            🤖 IA Predice
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                            {race.prediccion_top4.slice(0, 4).map((p, i) => (
                                <div key={i} style={{
                                    color: 'var(--text-main)',
                                    fontSize: '0.8rem',
                                    padding: '0.2rem 0.4rem',
                                    background: i === 0 ? 'rgba(99, 102, 241, 0.15)' : 'transparent',
                                    borderRadius: '4px',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '0.3rem'
                                }}>
                                    <span style={{
                                        color: i === 0 ? 'var(--primary)' : 'var(--text-muted)',
                                        fontWeight: i === 0 ? 700 : 400,
                                        minWidth: '1.2rem'
                                    }}>{i + 1}.</span>
                                    <span style={{ fontWeight: i === 0 ? 600 : 400 }}>{p}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                    <div>
                        <div style={{ color: 'var(--secondary)', marginBottom: '0.5rem', fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: 600 }}>
                            🏁 Resultado
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                            {race.resultado_top4.slice(0, 4).map((r, i) => (
                                <div key={i} style={{
                                    color: 'var(--text-main)',
                                    fontSize: '0.8rem',
                                    padding: '0.2rem 0.4rem',
                                    background: i === 0 ? 'rgba(52, 211, 153, 0.15)' : 'transparent',
                                    borderRadius: '4px',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '0.3rem'
                                }}>
                                    <span style={{
                                        color: i === 0 ? 'var(--secondary)' : 'var(--text-muted)',
                                        fontWeight: i === 0 ? 700 : 400,
                                        minWidth: '1.2rem'
                                    }}>{i + 1}.</span>
                                    <span style={{ fontWeight: i === 0 ? 600 : 400 }}>{r}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default async function PrecisionPage() {
    const data = await getPerformanceData()

    if (!data) {
        return (
            <div className="glass-card" style={{ textAlign: 'center', padding: '3rem' }}>
                <h2>⏳ Cargando datos de rendimiento...</h2>
                <p>Los datos de rendimiento aún no están disponibles.</p>
            </div>
        )
    }

    const stats = data.global.all_time
    const hipodromos = Object.entries(data.by_hipodromo)
        .sort((a, b) => b[1].total_carreras - a[1].total_carreras)

    return (
        <>
            {/* Hero Section */}
            <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
                <h1 style={{
                    fontSize: 'clamp(1.75rem, 5vw, 2.5rem)',
                    color: 'var(--text-main)',
                    marginBottom: '0.5rem',
                    fontWeight: 800
                }}>
                    📊 Rendimiento de Pista Inteligente
                </h1>
                <p style={{
                    color: 'var(--text-muted)',
                    fontSize: 'clamp(0.95rem, 2.5vw, 1.1rem)',
                    maxWidth: '800px',
                    margin: '0 auto',
                    lineHeight: 1.5
                }}>
                    <strong>Transparencia total</strong>: Comparamos nuestras predicciones con los resultados reales.
                    Sin manipulaciones, solo datos verificables.
                </p>
            </div>

            {/* Global Stats */}
            <div className="glass-card" style={{ marginBottom: '2rem', padding: '1.5rem' }}>
                <div className="section-title" style={{ marginBottom: '1.5rem' }}>
                    🎯 Precisión Global ({stats.total_carreras} carreras analizadas)
                </div>

                <div className="stats-container" style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
                    gap: '1rem'
                }}>
                    <StatCard
                        label="🥇 GANADOR"
                        value={stats.ganador_pct}
                        count={stats.ganador_count}
                        total={stats.total_carreras}
                        color="#FFD700"
                    />
                    <StatCard
                        label="🎯 QUINIELA"
                        value={stats.quiniela_pct}
                        count={stats.quiniela_count}
                        total={stats.total_carreras}
                        color="#C0C0C0"
                    />
                    <StatCard
                        label="🏆 TRIFECTA"
                        value={stats.trifecta_pct}
                        count={stats.trifecta_count}
                        total={stats.total_carreras}
                        color="#CD7F32"
                    />
                    <StatCard
                        label="⭐ SUPERFECTA"
                        value={stats.superfecta_pct}
                        count={stats.superfecta_count}
                        total={stats.total_carreras}
                        color="var(--primary)"
                    />
                </div>
            </div>


            {/* By Hipódromo */}
            <div className="glass-card" style={{ marginBottom: '2rem', padding: '1.5rem' }}>
                <div className="section-title" style={{ marginBottom: '1.5rem' }}>
                    🏇 Rendimiento por Hipódromo
                </div>

                <div className="hipodromo-list">
                    {hipodromos.map(([name, hipStats]) => (
                        <HipodromoCard key={name} name={name} stats={hipStats} />
                    ))}
                </div>
            </div>

            {/* Recent Races by Hipódromo (Accordion) */}
            <div style={{ marginBottom: '2rem' }}>
                <div className="section-title" style={{ marginBottom: '1rem', paddingLeft: '0.5rem' }}>
                    📋 Últimas Carreras Verificadas
                </div>

                {(() => {
                    // Filter races to show only those with at least one successful prediction
                    const filteredRaces = data.recent_races.filter(race =>
                        race.acierto_ganador || race.acierto_quiniela ||
                        race.acierto_trifecta || race.acierto_superfecta
                    )

                    // Group races by hipódromo
                    const racesByHipodromo: { [key: string]: RaceResult[] } = {}
                    filteredRaces.forEach(race => {
                        if (!racesByHipodromo[race.hipodromo]) {
                            racesByHipodromo[race.hipodromo] = []
                        }
                        racesByHipodromo[race.hipodromo].push(race)
                    })

                    // Sort hipódromos by most recent race date
                    const sortedHipodromos = Object.entries(racesByHipodromo)
                        .sort((a, b) => {
                            const latestA = a[1][0]?.fecha || ''
                            const latestB = b[1][0]?.fecha || ''
                            return latestB.localeCompare(latestA)
                        })

                    const getIcon = (hip: string) => {
                        if (hip.includes('Chile')) return '🏇'
                        if (hip.includes('Club')) return '🏛️'
                        if (hip.includes('Valparaíso')) return '🌊'
                        if (hip.includes('Concepción')) return '🌲'
                        return '🏇'
                    }

                    return sortedHipodromos.map(([hipodromo, races]) => {
                        // Sort races by date desc, then by race number
                        const sortedRaces = [...races].sort((a, b) => {
                            const dateCompare = b.fecha.localeCompare(a.fecha)
                            if (dateCompare !== 0) return dateCompare
                            return a.nro_carrera - b.nro_carrera
                        })

                        // Group by date
                        const racesByDate: { [key: string]: RaceResult[] } = {}
                        sortedRaces.forEach(race => {
                            if (!racesByDate[race.fecha]) {
                                racesByDate[race.fecha] = []
                            }
                            racesByDate[race.fecha].push(race)
                        })

                        const sortedDates = Object.keys(racesByDate).sort((a, b) => b.localeCompare(a))

                        // Calculate stats for this hipódromo — count ALL match types
                        const totalRaces = races.length
                        const ganadorCount = races.filter(r => r.acierto_ganador).length
                        const quinielaCount = races.filter(r => r.acierto_quiniela).length
                        const trifectaCount = races.filter(r => r.acierto_trifecta).length
                        const superfectaCount = races.filter(r => r.acierto_superfecta).length
                        const totalAciertos = ganadorCount + quinielaCount + trifectaCount + superfectaCount

                        return (
                            <details key={hipodromo} className="glass-card" style={{ marginBottom: '1rem' }} open>
                                <summary style={{
                                    cursor: 'pointer',
                                    padding: '1rem 1.25rem',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '0.75rem',
                                    listStyle: 'none',
                                    userSelect: 'none'
                                }}>
                                    <span style={{ fontSize: '1.5rem' }}>{getIcon(hipodromo)}</span>
                                    <div style={{ flex: 1 }}>
                                        <div style={{ fontWeight: 700, color: 'var(--text-main)', fontSize: '1.1rem' }}>
                                            {hipodromo}
                                        </div>
                                        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                                            {totalRaces} carreras • 🥇{ganadorCount} 🎯{quinielaCount} 🏆{trifectaCount} ⭐{superfectaCount}
                                        </div>
                                    </div>
                                    <div style={{
                                        background: 'rgba(99, 102, 241, 0.15)',
                                        color: 'var(--primary)',
                                        padding: '0.25rem 0.75rem',
                                        borderRadius: '20px',
                                        fontSize: '0.8rem',
                                        fontWeight: 600
                                    }}>
                                        {totalAciertos} aciertos
                                    </div>
                                    <span style={{ fontSize: '1.2rem', color: 'var(--text-muted)' }}>▼</span>
                                </summary>

                                <div style={{ padding: '0 1rem 1rem' }}>
                                    {sortedDates.map(fecha => {
                                        const dateRaces = racesByDate[fecha]
                                        const d = new Date(fecha + 'T12:00:00')
                                        const formattedDate = d.toLocaleDateString('es-CL', {
                                            weekday: 'long',
                                            day: 'numeric',
                                            month: 'long',
                                            year: 'numeric'
                                        })

                                        return (
                                            <div key={fecha} style={{ marginBottom: '1rem' }}>
                                                <div style={{
                                                    color: 'var(--text-muted)',
                                                    fontSize: '0.85rem',
                                                    fontWeight: 600,
                                                    textTransform: 'capitalize',
                                                    marginBottom: '0.5rem',
                                                    paddingBottom: '0.25rem',
                                                    borderBottom: '1px solid rgba(255,255,255,0.1)'
                                                }}>
                                                    📅 {formattedDate}
                                                </div>
                                                <div style={{
                                                    display: 'grid',
                                                    gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
                                                    gap: '0.75rem'
                                                }}>
                                                    {dateRaces.map(race => (
                                                        <RaceResultCard key={`${race.fecha}-${race.nro_carrera}`} race={race} />
                                                    ))}
                                                </div>
                                            </div>
                                        )
                                    })}
                                </div>
                            </details>
                        )
                    })
                })()}

                <div style={{
                    marginTop: '1rem',
                    padding: '1rem',
                    background: 'rgba(255,255,255,0.05)',
                    borderRadius: '12px',
                    textAlign: 'center',
                    border: '1px solid rgba(255,255,255,0.1)'
                }}>
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                        Mostrando carreras verificadas de 2026
                    </span>
                </div>
            </div>

            {/* Ad Banner - After Verified Races */}
            <AdBannerHorizontal />

            {/* Transparency Section */}
            <div className="glass-card" style={{ marginBottom: '2rem', padding: '1.5rem' }}>
                <div className="section-title" style={{ marginBottom: '1rem' }}>🔍 Nuestro Compromiso</div>

                <div className="commitment-grid" style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                    gap: '1rem'
                }}>
                    <div style={{
                        padding: '1.25rem',
                        background: 'rgba(52, 211, 153, 0.1)',
                        borderRadius: '12px',
                        borderLeft: '3px solid var(--secondary)'
                    }}>
                        <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>✅</div>
                        <h4 style={{ color: 'var(--secondary)', marginBottom: '0.5rem', fontSize: '1rem' }}>100% Verificable</h4>
                        <p style={{ color: 'var(--text-muted)', margin: 0, fontSize: '0.9rem' }}>
                            Cada predicción se registra ANTES de la carrera y se compara con resultados oficiales.
                        </p>
                    </div>

                    <div style={{
                        padding: '1.25rem',
                        background: 'rgba(99, 102, 241, 0.1)',
                        borderRadius: '12px',
                        borderLeft: '3px solid var(--primary)'
                    }}>
                        <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>📊</div>
                        <h4 style={{ color: 'var(--primary)', marginBottom: '0.5rem', fontSize: '1rem' }}>Datos Reales</h4>
                        <p style={{ color: 'var(--text-muted)', margin: 0, fontSize: '0.9rem' }}>
                            No manipulamos cifras. Mostramos la precisión calculada desde resultados oficiales de Teletrak.
                        </p>
                    </div>

                    <div style={{
                        padding: '1.25rem',
                        background: 'rgba(251, 191, 36, 0.1)',
                        borderRadius: '12px',
                        borderLeft: '3px solid var(--accent)'
                    }}>
                        <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>🎯</div>
                        <h4 style={{ color: 'var(--accent)', marginBottom: '0.5rem', fontSize: '1rem' }}>Mejora Continua</h4>
                        <p style={{ color: 'var(--text-muted)', margin: 0, fontSize: '0.9rem' }}>
                            Nuestro modelo de IA aprende de cada carrera. Actualizamos algoritmos constantemente.
                        </p>
                    </div>
                </div>
            </div>

            {/* CTA */}
            <div style={{
                textAlign: 'center',
                padding: '2rem 1rem',
                background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(52, 211, 153, 0.1))',
                borderRadius: '16px',
                marginBottom: '2rem'
            }}>
                <h2 style={{
                    color: 'var(--text-main)',
                    marginBottom: '1rem',
                    fontSize: 'clamp(1.25rem, 4vw, 1.75rem)'
                }}>
                    ¿Listo para las predicciones de hoy?
                </h2>
                <div style={{
                    display: 'flex',
                    flexWrap: 'wrap',
                    gap: '1rem',
                    justifyContent: 'center',
                    alignItems: 'center'
                }}>
                    <Link href="/programa" className="cta-button" style={{ display: 'inline-block' }}>
                        Ver Predicciones de Hoy
                    </Link>
                    <BotonQuinela linkPago="https://link.mercadopago.cl/pistainteligente" />
                </div>
            </div>
        </>
    )
}
