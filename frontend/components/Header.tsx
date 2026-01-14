'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

export default function Header() {
    const pathname = usePathname()

    return (
        <header className="glass-header">
            <Link href="/" className="brand">
                <img
                    src="/logo.png"
                    alt="Logo Pista Inteligente"
                    loading="eager"
                    style={{ height: '40px', borderRadius: '50%' }}
                />
                <span>Pista Inteligente</span>
            </Link>
            <nav className="nav-links">
                <Link href="/" className={`nav-link ${pathname === '/' ? 'active' : ''}`}>
                    Inicio
                </Link>
                <Link href="/programa" className={`nav-link ${pathname === '/programa' ? 'active' : ''}`}>
                    Predicciones
                </Link>
                <Link href="/precision" className={`nav-link ${pathname === '/precision' ? 'active' : ''}`}>
                    Precisión
                </Link>
                <Link href="/analisis" className={`nav-link ${pathname === '/analisis' ? 'active' : ''}`}>
                    Patrones
                </Link>
                <Link href="/estadisticas" className={`nav-link ${pathname === '/estadisticas' ? 'active' : ''}`}>
                    Estadísticas
                </Link>
            </nav>
        </header>
    )
}
