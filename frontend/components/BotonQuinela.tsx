'use client'

import { useState } from 'react'

interface BotonQuinelaProps {
    linkPago: string
}

export default function BotonQuinela({ linkPago }: BotonQuinelaProps) {
    const [isHovered, setIsHovered] = useState(false)

    const handleClick = () => {
        if (typeof window !== 'undefined') {
            window.open(linkPago, '_blank', 'noopener,noreferrer')
        }
    }

    return (
        <button
            onClick={handleClick}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
            className="quinela-button"
            title="Ayúdanos a mantener el servidor corriendo"
            style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.75rem',
                padding: '0.875rem 1.5rem',
                background: isHovered
                    ? 'linear-gradient(135deg, #22c55e 0%, #16a34a 50%, #15803d 100%)'
                    : 'linear-gradient(135deg, #16a34a 0%, #15803d 50%, #166534 100%)',
                border: '2px solid rgba(255, 255, 255, 0.15)',
                borderRadius: '12px',
                cursor: 'pointer',
                fontFamily: "'Outfit', 'Inter', sans-serif",
                fontSize: '0.95rem',
                fontWeight: 600,
                color: '#ffffff',
                boxShadow: isHovered
                    ? '0 0 25px rgba(34, 197, 94, 0.5), 0 8px 20px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.2)'
                    : '0 4px 15px rgba(22, 163, 74, 0.3), 0 6px 12px rgba(0, 0, 0, 0.2)',
                backdropFilter: 'blur(10px)',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                transform: isHovered ? 'translateY(-3px) scale(1.02)' : 'translateY(0) scale(1)',
                position: 'relative',
                overflow: 'hidden',
            }}
        >
            {/* Ticket/Boleto SVG Icon */}
            <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                style={{
                    transition: 'transform 0.3s ease',
                    transform: isHovered ? 'rotate(-5deg) scale(1.1)' : 'rotate(0deg) scale(1)',
                    filter: isHovered ? 'drop-shadow(0 0 6px rgba(255, 255, 255, 0.6))' : 'none',
                }}
            >
                {/* Ticket shape */}
                <path
                    d="M4 4h16a2 2 0 0 1 2 2v3a2 2 0 0 0 0 4v3a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-3a2 2 0 0 0 0-4V6a2 2 0 0 1 2-2z"
                    fill="rgba(255, 255, 255, 0.2)"
                    stroke="currentColor"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                />
                {/* Dotted line */}
                <path
                    d="M9 4v2M9 10v2M9 16v2"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeDasharray="2 2"
                />
                {/* Horseshoe symbol */}
                <path
                    d="M14 9c-1.5 0-2.5 1-2.5 2.5c0 1.2 0.8 2 1.5 2.5M16 9c1.5 0 2.5 1 2.5 2.5c0 1.2-0.8 2-1.5 2.5"
                    stroke="currentColor"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                    fill="none"
                />
                {/* Star/luck element */}
                <circle cx="15" cy="11" r="0.5" fill="currentColor" />
            </svg>

            {/* Text */}
            <span
                style={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'flex-start',
                    lineHeight: 1.2,
                }}
            >
                <span style={{ fontSize: '0.75rem', opacity: 0.85, fontWeight: 500 }}>
                    ¿Te sirvió el dato?
                </span>
                <span style={{ fontWeight: 700 }}>
                    Invítanos una Quinela 🎰
                </span>
            </span>

            {/* Animated shine effect */}
            <span
                style={{
                    position: 'absolute',
                    top: 0,
                    left: isHovered ? '100%' : '-100%',
                    width: '100%',
                    height: '100%',
                    background: 'linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent)',
                    transition: 'left 0.5s ease',
                    pointerEvents: 'none',
                }}
            />
        </button>
    )
}
