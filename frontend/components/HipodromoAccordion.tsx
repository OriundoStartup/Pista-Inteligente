'use client'

import { useState } from 'react'

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

interface HipodromoAccordionProps {
    hipodromos: [string, Carrera[]][]
    today: string
}

export default function HipodromoAccordion({ hipodromos, today }: HipodromoAccordionProps) {
    // Encontrar hipódromos con carreras del día actual
    const todayHipodromos = hipodromos
        .filter(([_, carreras]) => carreras.some(c => c.fecha === today))
        .map(([name]) => name)

    // Por defecto, abrir los hipódromos del día actual (o el primero si no hay ninguno hoy)
    const defaultOpen = todayHipodromos.length > 0
        ? new Set(todayHipodromos)
        : new Set(hipodromos.slice(0, 1).map(([name]) => name))

    const [openHipodromos, setOpenHipodromos] = useState<Set<string>>(defaultOpen)

    const toggleHipodromo = (name: string) => {
        setOpenHipodromos(prev => {
            const newSet = new Set(prev)
            if (newSet.has(name)) {
                newSet.delete(name)
            } else {
                newSet.add(name)
            }
            return newSet
        })
    }

    const isToday = (fecha: string) => fecha === today

    return (
        <>
            {hipodromos.map(([hipodromo, carrerasHip]) => {
                const isOpen = openHipodromos.has(hipodromo)
                const hasToday = carrerasHip.some(c => isToday(c.fecha))

                return (
                    <div
                        key={hipodromo}
                        className="glass-card accordion-card"
                        style={{
                            marginBottom: '1.5rem',
                            padding: 0,
                            borderLeft: hasToday ? '4px solid var(--secondary)' : '4px solid var(--primary)',
                            overflow: 'hidden'
                        }}
                    >
                        {/* Header clickeable del Hipódromo */}
                        <div
                            className="accordion-header"
                            onClick={() => toggleHipodromo(hipodromo)}
                            style={{
                                padding: '1.25rem 1.5rem',
                                display: 'flex',
                                justifyContent: 'space-between',
                                alignItems: 'center',
                                flexWrap: 'wrap',
                                gap: '0.75rem',
                                background: isOpen ? 'rgba(139, 92, 246, 0.05)' : 'transparent'
                            }}
                        >
                            <div style={{ flex: '1 1 auto', minWidth: '200px' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
                                    <h2 style={{
                                        color: 'var(--text-main)',
                                        fontSize: 'clamp(1.2rem, 4vw, 1.8rem)',
                                        fontWeight: 800,
                                        margin: 0,
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '0.5rem',
                                        textShadow: '0 0 20px rgba(139, 92, 246, 0.3)'
                                    }}>
                                        🏇 {hipodromo}
                                    </h2>
                                    {hasToday && (
                                        <span className="badge-today">
                                            📅 HOY
                                        </span>
                                    )}
                                </div>
                                <p style={{
                                    color: 'var(--text-muted)',
                                    margin: '0.25rem 0 0 0',
                                    fontSize: 'clamp(0.8rem, 2.5vw, 1rem)'
                                }}>
                                    📅 {carrerasHip[0]?.fecha} • {carrerasHip.length} Carreras
                                </p>
                            </div>

                            {/* Chevron y badge */}
                            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                <div style={{
                                    background: 'rgba(139, 92, 246, 0.1)',
                                    padding: '0.4rem 0.8rem',
                                    borderRadius: '50px',
                                    border: '1px solid rgba(139, 92, 246, 0.2)',
                                    color: 'var(--primary)',
                                    fontWeight: '600',
                                    fontSize: 'clamp(0.7rem, 2vw, 0.85rem)',
                                    whiteSpace: 'nowrap'
                                }}>
                                    Programa Oficial
                                </div>
                                <span
                                    className={`accordion-chevron ${isOpen ? 'open' : ''}`}
                                    style={{
                                        fontSize: '1.5rem',
                                        color: 'var(--primary)',
                                        display: 'flex',
                                        alignItems: 'center'
                                    }}
                                >
                                    ▼
                                </span>
                            </div>
                        </div>

                        {/* Contenido colapsable */}
                        <div className={`accordion-content ${isOpen ? 'open' : ''}`}>
                            <div style={{
                                padding: '0 1.5rem 1.5rem',
                                display: 'flex',
                                flexDirection: 'column',
                                gap: '1.5rem'
                            }}>
                                {carrerasHip.sort((a, b) => a.carrera - b.carrera).map((carrera) => (
                                    <div key={carrera.id} className="carrera-card" style={{
                                        padding: 'clamp(0.75rem, 3vw, 1.5rem)',
                                        background: 'rgba(255,255,255,0.02)',
                                        borderRadius: '12px',
                                        border: '1px solid rgba(255, 255, 255, 0.05)'
                                    }}>
                                        <div style={{
                                            marginBottom: '1rem',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'space-between',
                                            flexWrap: 'wrap',
                                            gap: '0.5rem'
                                        }}>
                                            <h3 style={{
                                                color: 'var(--secondary)',
                                                margin: 0,
                                                fontSize: 'clamp(1rem, 3vw, 1.3rem)',
                                                fontWeight: 700
                                            }}>
                                                Carrera {carrera.carrera}
                                            </h3>
                                            <div style={{
                                                display: 'flex',
                                                gap: '0.75rem',
                                                fontSize: 'clamp(0.75rem, 2.5vw, 0.9rem)',
                                                color: 'var(--text-muted)',
                                                flexWrap: 'wrap'
                                            }}>
                                                <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                                                    🕒 {carrera.hora}
                                                </span>
                                                <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                                                    🏁 {carrera.distancia}m
                                                </span>
                                            </div>
                                        </div>

                                        {/* Tabla responsive */}
                                        <div className="table-responsive">
                                            <table className="modern-table">
                                                <thead>
                                                    <tr>
                                                        <th style={{ width: '40px', textAlign: 'center' }}>#</th>
                                                        <th>Caballo</th>
                                                        <th className="hide-mobile">Jinete</th>
                                                        <th>IA Score</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {carrera.predicciones.map((pred, index) => (
                                                        <tr key={index}>
                                                            <td style={{ textAlign: 'center', fontWeight: 'bold', color: 'var(--text-muted)' }}>
                                                                {pred.numero}
                                                            </td>
                                                            <td style={{ fontWeight: 600, color: 'var(--text-main)' }}>
                                                                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                                                                    <span>
                                                                        {pred.caballo}
                                                                        {index === 0 && (
                                                                            <span style={{
                                                                                marginLeft: '0.5rem',
                                                                                fontSize: '0.7rem',
                                                                                background: '#eab308',
                                                                                color: 'black',
                                                                                padding: '1px 5px',
                                                                                borderRadius: '4px',
                                                                                fontWeight: 'bold'
                                                                            }}>
                                                                                FAV
                                                                            </span>
                                                                        )}
                                                                    </span>
                                                                    {/* Jinete visible solo en mobile como línea secundaria */}
                                                                    <span className="show-mobile-only" style={{
                                                                        fontSize: '0.75rem',
                                                                        color: 'var(--text-muted)'
                                                                    }}>
                                                                        {pred.jinete}
                                                                    </span>
                                                                </div>
                                                            </td>
                                                            <td className="hide-mobile" style={{ color: 'var(--text-muted)' }}>
                                                                {pred.jinete}
                                                            </td>
                                                            <td>
                                                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                                                    <div style={{ flexGrow: 1, minWidth: '60px', maxWidth: '150px' }}>
                                                                        <div style={{
                                                                            display: 'flex',
                                                                            justifyContent: 'space-between',
                                                                            fontSize: '0.7rem',
                                                                            marginBottom: '2px'
                                                                        }}>
                                                                            <span style={{ color: 'var(--text-muted)' }}>Confianza</span>
                                                                            <span style={{
                                                                                fontWeight: 'bold',
                                                                                color: pred.puntaje_ia > 80 ? '#4ade80' : pred.puntaje_ia > 50 ? '#fbbf24' : '#f87171'
                                                                            }}>
                                                                                {pred.puntaje_ia.toFixed(0)}%
                                                                            </span>
                                                                        </div>
                                                                        <div style={{
                                                                            background: 'rgba(255,255,255,0.1)',
                                                                            height: '4px',
                                                                            borderRadius: '10px',
                                                                            overflow: 'hidden'
                                                                        }}>
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
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )
            })}
        </>
    )
}
