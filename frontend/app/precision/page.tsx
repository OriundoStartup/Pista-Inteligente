import Link from 'next/link'
import type { Metadata } from 'next'
import { promises as fs } from 'fs'
import path from 'path'
import BotonQuinela from '@/components/BotonQuinela'

export const metadata: Metadata = {
    title: 'Rendimiento Pista Inteligente - Precisión Real | Predicciones Hípicas IA',
    description: 'Transparencia total: Conoce el rendimiento real de Pista Inteligente. Ganador exacto, Quiniela, Trifecta y Superfecta por hipódromo.',
}

export const revalidate = 3600 // Revalidar cada hora

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
        const filePath = path.join(process.cwd(), '..', 'data', 'rendimiento_stats.json')
        const fileContents = await fs.readFile(filePath, 'utf8')
        return JSON.parse(fileContents) as PerformanceData
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

function RaceResultRow({ race }: { race: RaceResult }) {
    const formatDate = (fecha: string) => {
        const d = new Date(fecha + 'T12:00:00')
        return d.toLocaleDateString('es-CL', { day: '2-digit', month: 'short' })
    }

    const getShortName = (hip: string) => {
        if (hip.includes('Hipódromo Chile')) return 'H. Chile'
        if (hip.includes('Club Hípico de Santiago')) return 'C. Hípico'
        if (hip.includes('Valparaíso')) return 'Valparaíso'
        if (hip.includes('Concepción')) return 'Concepción'
        return hip.substring(0, 12)
    }

    return (
        <tr>
            <td style={{ whiteSpace: 'nowrap' }}>{formatDate(race.fecha)}</td>
            <td className="hide-mobile">{getShortName(race.hipodromo)}</td>
            <td style={{ textAlign: 'center' }}>C{race.nro_carrera}</td>
            <td style={{ textAlign: 'center' }}>{race.acierto_ganador ? '✅' : '❌'}</td>
            <td style={{ textAlign: 'center' }}>{race.acierto_quiniela ? '✅' : '❌'}</td>
            <td style={{ textAlign: 'center' }} className="hide-mobile">{race.acierto_trifecta ? '✅' : '❌'}</td>
            <td style={{ textAlign: 'center' }} className="hide-mobile">{race.acierto_superfecta ? '✅' : '❌'}</td>
        </tr>
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

            {/* Recent Races Table */}
            <div className="glass-card" style={{ marginBottom: '2rem', padding: '1.5rem' }}>
                <div className="section-title" style={{ marginBottom: '1rem' }}>
                    📋 Últimas Carreras Verificadas
                </div>

                <div className="table-container" style={{ overflowX: 'auto' }}>
                    <table className="modern-table" style={{ width: '100%', fontSize: '0.9rem' }}>
                        <thead>
                            <tr>
                                <th>Fecha</th>
                                <th className="hide-mobile">Hipódromo</th>
                                <th style={{ textAlign: 'center' }}>Carrera</th>
                                <th style={{ textAlign: 'center' }}>🥇</th>
                                <th style={{ textAlign: 'center' }}>🎯</th>
                                <th style={{ textAlign: 'center' }} className="hide-mobile">🏆</th>
                                <th style={{ textAlign: 'center' }} className="hide-mobile">⭐</th>
                            </tr>
                        </thead>
                        <tbody>
                            {data.recent_races.slice(0, 20).map((race, idx) => (
                                <RaceResultRow key={`${race.fecha}-${race.hipodromo}-${race.nro_carrera}`} race={race} />
                            ))}
                        </tbody>
                    </table>
                </div>

                <div style={{
                    marginTop: '1rem',
                    padding: '0.75rem',
                    background: 'rgba(255,255,255,0.05)',
                    borderRadius: '8px',
                    textAlign: 'center'
                }}>
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                        🥇 = Ganador Exacto | 🎯 = Quiniela | 🏆 = Trifecta | ⭐ = Superfecta
                    </span>
                </div>
            </div>

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

            {/* Mobile-specific styles */}
            <style jsx>{`
                @media (max-width: 640px) {
                    .hide-mobile {
                        display: none !important;
                    }
                    .stats-grid {
                        grid-template-columns: repeat(2, 1fr) !important;
                    }
                    .stat-card {
                        padding: 1rem !important;
                    }
                }
            `}</style>
        </>
    )
}
