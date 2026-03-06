'use client'

import { useEffect } from 'react'
import Link from 'next/link'

export default function Error({
    error,
    reset,
}: {
    error: Error & { digest?: string }
    reset: () => void
}) {
    useEffect(() => {
        console.error(error)
    }, [error])

    return (
        <div className="glass-card text-center" style={{ padding: '3rem', marginTop: '2rem' }}>
            <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>⚠️</div>
            <h2 style={{ color: 'var(--text-main)', marginBottom: '1rem' }}>Oh no, ocurrió un problema</h2>
            <p style={{ color: 'var(--text-muted)', marginBottom: '2rem', maxWidth: '400px', margin: '0 auto 2rem' }}>
                No pudimos cargar las predicciones en este momento. Esto puede deberse a un problema de conexión o a que los datos se están actualizando.
            </p>
            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
                <button
                    onClick={() => reset()}
                    className="cta-button"
                    style={{ border: 'none', cursor: 'pointer', fontFamily: 'inherit' }}
                >
                    Intentar de nuevo
                </button>
                <Link href="/" className="nav-link" style={{ padding: '1rem 2rem', border: '1px solid var(--primary)', borderRadius: '50px' }}>
                    Volver al Inicio
                </Link>
            </div>
        </div>
    )
}
