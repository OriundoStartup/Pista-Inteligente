'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useState, useEffect } from 'react'

export default function Header() {
    const pathname = usePathname()
    const [isMenuOpen, setIsMenuOpen] = useState(false)

    // Cerrar menú al cambiar de ruta
    useEffect(() => {
        setIsMenuOpen(false)
    }, [pathname])

    // Cerrar menú al hacer scroll
    useEffect(() => {
        const handleScroll = () => {
            if (isMenuOpen) setIsMenuOpen(false)
        }
        window.addEventListener('scroll', handleScroll)
        return () => window.removeEventListener('scroll', handleScroll)
    }, [isMenuOpen])

    // Prevenir scroll cuando el menú está abierto
    useEffect(() => {
        if (isMenuOpen) {
            document.body.style.overflow = 'hidden'
        } else {
            document.body.style.overflow = ''
        }
        return () => {
            document.body.style.overflow = ''
        }
    }, [isMenuOpen])

    const navLinks = [
        { href: '/', label: 'Inicio', icon: '🏠' },
        { href: '/programa', label: 'Predicciones', icon: '🔮' },
        { href: '/precision', label: 'Precisión', icon: '🎯' },
        { href: '/analisis', label: 'Patrones', icon: '📊' },
        { href: '/estadisticas', label: 'Estadísticas', icon: '📈' },
    ]

    return (
        <>
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

                {/* Desktop Navigation */}
                <nav className="nav-links nav-desktop">
                    {navLinks.map((link) => (
                        <Link
                            key={link.href}
                            href={link.href}
                            className={`nav-link ${pathname === link.href ? 'active' : ''}`}
                        >
                            {link.label}
                        </Link>
                    ))}
                </nav>

                {/* Mobile Menu Button */}
                <button
                    className="mobile-menu-btn"
                    onClick={() => setIsMenuOpen(!isMenuOpen)}
                    aria-label={isMenuOpen ? 'Cerrar menú' : 'Abrir menú'}
                    aria-expanded={isMenuOpen}
                >
                    <span className={`hamburger ${isMenuOpen ? 'open' : ''}`}>
                        <span></span>
                        <span></span>
                        <span></span>
                    </span>
                </button>
            </header>

            {/* Mobile Menu Overlay */}
            <div
                className={`mobile-menu-overlay ${isMenuOpen ? 'open' : ''}`}
                onClick={() => setIsMenuOpen(false)}
            />

            {/* Mobile Menu */}
            <nav className={`mobile-menu ${isMenuOpen ? 'open' : ''}`}>
                {navLinks.map((link) => (
                    <Link
                        key={link.href}
                        href={link.href}
                        className={`mobile-nav-link ${pathname === link.href ? 'active' : ''}`}
                        onClick={() => setIsMenuOpen(false)}
                    >
                        <span className="mobile-nav-icon">{link.icon}</span>
                        <span>{link.label}</span>
                    </Link>
                ))}
            </nav>
        </>
    )
}
