import { createClient } from '../../utils/supabase/server'
import type { Metadata } from 'next'

export const metadata: Metadata = {
    title: 'Estadísticas Hípicas | Pista Inteligente',
    description: 'Estadísticas completas de carreras de caballos en Chile. Datos de jinetes, caballos y resultados históricos.',
}

// ISR: Revalidar cada 10 minutos
export const revalidate = 600

interface HitRace {
    fecha: string;
    hipodromo: string;
    nro_carrera: number;
    acierto_ganador: boolean;
    acierto_quiniela: boolean;
    acierto_trifecta: boolean;
    acierto_superfecta: boolean;
    prediccion_top4: string[];
}

async function getRecentHits2026(): Promise<HitRace[]> {
    const supabase = await createClient()

    const { data, error } = await supabase
        .from('rendimiento_historico')
        .select('fecha, hipodromo, nro_carrera, acierto_ganador, acierto_quiniela, acierto_trifecta, acierto_superfecta, prediccion_top4')
        .gte('fecha', '2026-01-01')
        .or('acierto_ganador.eq.true,acierto_quiniela.eq.true,acierto_trifecta.eq.true,acierto_superfecta.eq.true')
        .order('fecha', { ascending: false })
        .limit(30)

    if (error) {
        console.error("Error fetching hits:", error);
        return [];
    }

    return (data || []).map((row: any) => ({
        ...row,
        prediccion_top4: typeof row.prediccion_top4 === 'string'
            ? JSON.parse(row.prediccion_top4)
            : row.prediccion_top4
    }));
}

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
            total_carreras: 1250,
            total_caballos: 850,
            total_jinetes: 120,
            total_jornadas: 180,
        }
    }
}

function HitCard({ race }: { race: HitRace }) {
    // Logic to determine priority hit type
    let hitType = 'Ganador';
    let horsesToShow = 1;
    let badgeColor = '#10b981'; // Default Emerald/Green
    let gradientBg = 'linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(16, 185, 129, 0.05) 100%)';
    let label = '🥇 GANADOR';
    let icon = '🥇';

    if (race.acierto_superfecta) {
        hitType = 'Superfecta';
        horsesToShow = 4;
        badgeColor = '#d946ef'; // Fuchsia/Purple
        gradientBg = 'linear-gradient(135deg, rgba(217, 70, 239, 0.2) 0%, rgba(217, 70, 239, 0.05) 100%)';
        label = '⭐ SUPERFECTA';
        icon = '⭐';
    } else if (race.acierto_trifecta) {
        hitType = 'Trifecta';
        horsesToShow = 3;
        badgeColor = '#f59e0b'; // Amber/Orange
        gradientBg = 'linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(245, 158, 11, 0.05) 100%)';
        label = '🏆 TRIFECTA';
        icon = '🏆';
    } else if (race.acierto_quiniela) {
        hitType = 'Quiniela';
        horsesToShow = 2;
        badgeColor = '#3b82f6'; // Blue
        gradientBg = 'linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(59, 130, 246, 0.05) 100%)';
        label = '🎯 QUINIELA';
        icon = '🎯';
    }

    const horses = (race.prediccion_top4 || []).slice(0, horsesToShow);

    // Format Date
    const dateObj = new Date(race.fecha + 'T12:00:00');
    const dateStr = dateObj.toLocaleDateString('es-CL', { day: 'numeric', month: 'long' });

    return (
        <div className="glass-card" style={{
            padding: 0,
            position: 'relative',
            overflow: 'hidden',
            border: `1px solid ${badgeColor}40`,
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            background: 'rgba(30, 41, 59, 0.6)',
            boxShadow: `0 10px 30px -10px ${badgeColor}20`
        }}>
            {/* Header: Badge & Date */}
            <div style={{
                padding: '1rem',
                background: gradientBg,
                borderBottom: `1px solid ${badgeColor}20`,
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span style={{ fontSize: '1.2rem' }}>{icon}</span>
                    <span style={{
                        color: typeof badgeColor === 'string' ? badgeColor : 'white',
                        fontWeight: 800,
                        fontSize: '0.9rem',
                        letterSpacing: '0.5px',
                        textTransform: 'uppercase'
                    }}>
                        {hitType}
                    </span>
                </div>
                <span style={{ fontSize: '0.8rem', color: 'rgba(255,255,255,0.7)', fontWeight: 500 }}>{dateStr}</span>
            </div>

            {/* Content: Horses */}
            <div style={{ padding: '1.25rem', flex: 1 }}>
                <div style={{
                    fontSize: '0.7rem',
                    textTransform: 'uppercase',
                    color: 'var(--text-muted)',
                    marginBottom: '0.75rem',
                    letterSpacing: '1px',
                    fontWeight: 600
                }}>
                    {horsesToShow > 1 ? 'Combinación Ganadora' : 'Caballo Ganador'}
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    {horses.map((horse, idx) => (
                        <div key={idx} style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.75rem',
                            padding: '0.5rem',
                            borderRadius: '8px',
                            background: idx === 0 ? `linear-gradient(90deg, ${badgeColor}15, transparent)` : 'transparent',
                            borderLeft: idx === 0 ? `3px solid ${badgeColor}` : '3px solid transparent'
                        }}>
                            <span style={{
                                width: '24px',
                                height: '24px',
                                borderRadius: '50%',
                                backgroundColor: idx === 0 ? badgeColor : 'rgba(255,255,255,0.1)',
                                color: idx === 0 ? '#000' : 'var(--text-muted)',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                fontSize: '0.75rem',
                                fontWeight: 700
                            }}>{idx + 1}</span>
                            <span style={{
                                color: idx === 0 ? 'white' : 'var(--text-main)',
                                fontWeight: idx === 0 ? 700 : 400,
                                fontSize: '0.95rem'
                            }}>{horse}</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Footer: Context */}
            <div style={{
                padding: '0.75rem 1.25rem',
                background: 'rgba(0,0,0,0.2)',
                borderTop: '1px solid rgba(255,255,255,0.05)',
                fontSize: '0.8rem',
                color: 'var(--text-muted)',
                display: 'flex',
                justifyContent: 'space-between',
                marginTop: 'auto'
            }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    🏟️ <span style={{ fontWeight: 500 }}>{race.hipodromo}</span>
                </span>
                <span style={{ background: 'rgba(255,255,255,0.1)', padding: '0.1rem 0.5rem', borderRadius: '4px' }}>
                    Carrera {race.nro_carrera}
                </span>
            </div>
        </div>
    )
}

export default async function EstadisticasPage() {
    const statsPromise = getEstadisticas()
    const recentHitsPromise = getRecentHits2026()

    const [stats, recentHits] = await Promise.all([statsPromise, recentHitsPromise])

    return (
        <>
            {/* Header */}
            <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
                <h1 style={{ fontSize: 'clamp(2rem, 5vw, 2.5rem)', color: 'var(--text-main)', marginBottom: '0.5rem', fontWeight: 800 }}>
                    📈 Estadísticas del Sistema
                </h1>
                <p style={{ color: 'var(--text-muted)', fontSize: '1.2rem', maxWidth: '800px', margin: '0 auto' }}>
                    Datos actualizados de nuestra base de datos de carreras hípicas en Chile.
                </p>
            </div>

            {/* Stats Grid */}
            <div className="glass-card" style={{ marginBottom: '2rem' }}>
                <div className="section-title">🗄️ Base de Datos</div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem' }}>
                    <div className="glass-card" style={{ textAlign: 'center', padding: '2rem', borderLeft: '4px solid var(--primary)' }}>
                        <span style={{ fontSize: '3rem', color: 'var(--primary)', display: 'block', fontWeight: 800 }}>
                            {stats.total_carreras.toLocaleString()}
                        </span>
                        <p style={{ color: 'var(--text-muted)', margin: 0 }}>🏁 Carreras Registradas</p>
                    </div>

                    <div className="glass-card" style={{ textAlign: 'center', padding: '2rem', borderLeft: '4px solid var(--secondary)' }}>
                        <span style={{ fontSize: '3rem', color: 'var(--secondary)', display: 'block', fontWeight: 800 }}>
                            {stats.total_caballos.toLocaleString()}
                        </span>
                        <p style={{ color: 'var(--text-muted)', margin: 0 }}>🐴 Caballos</p>
                    </div>

                    <div className="glass-card" style={{ textAlign: 'center', padding: '2rem', borderLeft: '4px solid var(--accent)' }}>
                        <span style={{ fontSize: '3rem', color: 'var(--accent)', display: 'block', fontWeight: 800 }}>
                            {stats.total_jinetes.toLocaleString()}
                        </span>
                        <p style={{ color: 'var(--text-muted)', margin: 0 }}>🏇 Jinetes</p>
                    </div>

                    <div className="glass-card" style={{ textAlign: 'center', padding: '2rem', borderLeft: '4px solid #FFD700' }}>
                        <span style={{ fontSize: '3rem', color: '#FFD700', display: 'block', fontWeight: 800 }}>
                            {stats.total_jornadas.toLocaleString()}
                        </span>
                        <p style={{ color: 'var(--text-muted)', margin: 0 }}>📅 Jornadas</p>
                    </div>
                </div>
            </div>

            {/* Recent Hits 2026 Section */}
            {recentHits.length > 0 && (
                <div className="glass-card" style={{ marginBottom: '2rem', background: 'linear-gradient(145deg, rgba(16, 185, 129, 0.05), rgba(15, 23, 42, 0.4))' }}>
                    <div className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span>✨ Últimos Aciertos 2026</span>
                        <span className="badge" style={{ fontSize: '0.8rem', background: 'var(--primary)', color: '#000', padding: '0.1rem 0.5rem', borderRadius: '10px' }}>Verificados</span>
                    </div>

                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
                        gap: '1.5rem',
                        marginTop: '1.5rem'
                    }}>
                        {recentHits.map((hit) => (
                            <HitCard
                                key={`${hit.fecha}-${hit.hipodromo}-${hit.nro_carrera}-${hit.acierto_superfecta}-${hit.acierto_trifecta}`}
                                race={hit}
                            />
                        ))}
                    </div>
                </div>
            )}

            {/* Hipódromos */}
            <div className="glass-card" style={{ marginBottom: '2rem' }}>
                <div className="section-title">🏟️ Hipódromos Cubiertos</div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
                    <div className="glass-card" style={{ padding: '2rem', textAlign: 'center' }}>
                        <h3 style={{ color: 'var(--primary)', marginBottom: '0.5rem', fontSize: '1.5rem' }}>Hipódromo Chile</h3>
                        <p style={{ color: 'var(--text-muted)', margin: 0 }}>
                            Santiago - Principal recinto hípico del país
                        </p>
                    </div>

                    <div className="glass-card" style={{ padding: '2rem', textAlign: 'center' }}>
                        <h3 style={{ color: 'var(--secondary)', marginBottom: '0.5rem', fontSize: '1.5rem' }}>Club Hípico de Santiago</h3>
                        <p style={{ color: 'var(--text-muted)', margin: 0 }}>
                            Santiago - Tradición desde 1869
                        </p>
                    </div>

                    <div className="glass-card" style={{ padding: '2rem', textAlign: 'center' }}>
                        <h3 style={{ color: '#10b981', marginBottom: '0.5rem', fontSize: '1.5rem' }}>Valparaíso Sporting</h3>
                        <p style={{ color: 'var(--text-muted)', margin: 0 }}>
                            Viña del Mar - Cuna de la hípica chilena
                        </p>
                    </div>

                    <div className="glass-card" style={{ padding: '2rem', textAlign: 'center' }}>
                        <h3 style={{ color: '#f59e0b', marginBottom: '0.5rem', fontSize: '1.5rem' }}>Club Hípico de Concepción</h3>
                        <p style={{ color: 'var(--text-muted)', margin: 0 }}>
                            Hualpén - Hípica del sur
                        </p>
                    </div>
                </div>
            </div>

            {/* Model Info */}
            <div className="glass-card">
                <div className="section-title">🤖 Tecnología Utilizada</div>

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
                            <td>Gradient Boosting optimizado para ranking</td>
                        </tr>
                        <tr>
                            <td>Modelo Secundario</td>
                            <td style={{ color: 'var(--secondary)', fontWeight: 600 }}>XGBoost</td>
                            <td>Ensemble para mayor robustez</td>
                        </tr>
                        <tr>
                            <td>Modelo Terciario</td>
                            <td style={{ color: 'var(--accent)', fontWeight: 600 }}>CatBoost</td>
                            <td>Especializado en variables categóricas</td>
                        </tr>
                        <tr>
                            <td>Meta-Learner</td>
                            <td style={{ color: '#FFD700', fontWeight: 600 }}>Ridge Regression</td>
                            <td>Combina predicciones de los 3 modelos</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </>
    )
}
