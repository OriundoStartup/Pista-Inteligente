import Link from 'next/link'
import type { Metadata } from 'next'
import PatronesList from '@/components/PatronesList'
import { AdBannerHorizontal } from '@/components/AdSense'

export const metadata: Metadata = {
    title: 'Patrones de Carreras - Análisis con IA | Pista Inteligente',
    description: 'Descubre patrones ocultos en las carreras de caballos del Hipódromo Chile y Club Hípico. Análisis profundo con Inteligencia Artificial.',
}

export default function AnalisisPage() {
    const patrones = [
        { titulo: 'Ventaja del Riel Interior', descripcion: 'Caballos en posición 1-3 tienen 15% más probabilidad de ganar en distancias cortas.', impacto: 'Alto' },
        { titulo: 'Factor Jinete-Caballo', descripcion: 'Combinaciones jinete-caballo con historial positivo mejoran 22% las chances.', impacto: 'Alto' },
        { titulo: 'Descenso de Categoría', descripcion: 'Caballos que bajan de categoría en su última carrera muestran 18% mejor rendimiento.', impacto: 'Medio' },
        { titulo: 'Descanso Óptimo', descripcion: 'Caballos con 21-35 días de descanso rinden mejor que los que corren más seguido.', impacto: 'Medio' },
        { titulo: 'Condición de Pista', descripcion: 'Algunos caballos rinden 25% mejor en pista húmeda vs seca.', impacto: 'Alto' },
    ]

    return (
        <>
            {/* Header */}
            <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
                <h1 style={{ fontSize: '2.5rem', color: 'var(--text-main)', marginBottom: '0.5rem', fontWeight: 800 }}>
                    🔍 Patrones Detectados por IA
                </h1>
                <p style={{ color: 'var(--text-muted)', fontSize: '1.2rem', maxWidth: '800px', margin: '0 auto' }}>
                    Nuestro sistema analiza los resultados de los últimos 60 días en <strong>todos los hipódromos</strong> para encontrar números que se repiten.
                </p>
            </div>

            {/* Dynamic Patterns Section */}
            <div className="glass-card mb-8">
                <div className="section-title flex items-center gap-2">
                    <span>🎰</span> Patrones Numéricos en Vivo
                </div>
                <div className="mb-4 text-gray-400 text-sm">
                    Estos números (mandiles) han formado combinaciones ganadoras (Quinelas, Trifectas, Superfectas) al menos 2 veces recientemente.
                </div>
                <PatronesList />
            </div>

            {/* Ad Banner - After Live Patterns */}
            <AdBannerHorizontal />

            {/* Patrones Grid (Teoría) */}
            <div className="glass-card" style={{ marginBottom: '2rem' }}>
                <div className="section-title">📚 Factores Estadísticos Generales</div>

                <div style={{ display: 'grid', gap: '1rem' }}>
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
                                <h3 style={{ color: 'var(--text-main)', margin: 0, fontSize: '1.2rem' }}>{patron.titulo}</h3>
                                <span
                                    style={{
                                        background: patron.impacto === 'Alto' ? 'rgba(139, 92, 246, 0.2)' : 'rgba(6, 182, 212, 0.2)',
                                        color: patron.impacto === 'Alto' ? 'var(--primary)' : 'var(--secondary)',
                                        padding: '0.25rem 0.75rem',
                                        borderRadius: '20px',
                                        fontSize: '0.8rem',
                                        fontWeight: 600
                                    }}
                                >
                                    Impacto {patron.impacto}
                                </span>
                            </div>
                            <p style={{ color: 'var(--text-muted)', margin: 0 }}>{patron.descripcion}</p>
                        </div>
                    ))}
                </div>
            </div>

            {/* How it Works */}
            <div className="glass-card" style={{ marginBottom: '2rem' }}>
                <div className="section-title">🤖 ¿Cómo Funciona Nuestro Análisis?</div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem' }}>
                    <div style={{ textAlign: 'center', padding: '2rem' }}>
                        <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📥</div>
                        <h3 style={{ color: 'var(--secondary)', marginBottom: '0.5rem' }}>1. Recolección</h3>
                        <p style={{ color: 'var(--text-muted)', margin: 0 }}>
                            Importamos datos de todas las carreras del Hipódromo Chile y Club Hípico.
                        </p>
                    </div>

                    <div style={{ textAlign: 'center', padding: '2rem' }}>
                        <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🧮</div>
                        <h3 style={{ color: 'var(--primary)', marginBottom: '0.5rem' }}>2. Procesamiento</h3>
                        <p style={{ color: 'var(--text-muted)', margin: 0 }}>
                            Nuestro modelo de ML procesa +50 variables por cada participante.
                        </p>
                    </div>

                    <div style={{ textAlign: 'center', padding: '2rem' }}>
                        <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🎯</div>
                        <h3 style={{ color: 'var(--accent)', marginBottom: '0.5rem' }}>3. Predicción</h3>
                        <p style={{ color: 'var(--text-muted)', margin: 0 }}>
                            Generamos un Score de Confianza para cada caballo antes de cada carrera.
                        </p>
                    </div>
                </div>
            </div>

            {/* Ad Banner - After How It Works */}
            <AdBannerHorizontal />

            {/* CTA */}
            <div style={{ textAlign: 'center', marginTop: '3rem', padding: '3rem 1rem', background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(52, 211, 153, 0.1))', borderRadius: '16px' }}>
                <h2 style={{ color: 'var(--text-main)', marginBottom: '1rem', fontSize: '2rem' }}>
                    Aprovecha estos patrones
                </h2>
                <Link href="/programa" className="cta-button" style={{ display: 'inline-block' }}>
                    Ver Predicciones de Hoy
                </Link>
            </div>
        </>
    )
}
