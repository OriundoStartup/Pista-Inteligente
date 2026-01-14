import Link from 'next/link'

export default function Footer() {
    return (
        <footer className="site-footer">
            <div className="footer-content">
                <p className="copyright">© 2025 Pista Inteligente. Todos los derechos reservados.</p>
                <div className="footer-links" style={{ marginBottom: '0.5rem' }}>
                    <Link
                        href="/quienes-somos"
                        style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginRight: '1rem', textDecoration: 'none' }}
                    >
                        Quiénes Somos
                    </Link>
                    <Link
                        href="/politica-de-privacidad"
                        style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginRight: '1rem', textDecoration: 'none' }}
                    >
                        Política de Privacidad
                    </Link>
                    <Link
                        href="/terminos-y-condiciones"
                        style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginRight: '1rem', textDecoration: 'none' }}
                    >
                        Términos y Condiciones
                    </Link>
                </div>
                <p className="credits">
                    Sitio creado por{' '}
                    <a href="https://oriundostartupchile.com" target="_blank" rel="noopener noreferrer">
                        oriundostartupchile.com
                    </a>
                </p>
            </div>
        </footer>
    )
}
