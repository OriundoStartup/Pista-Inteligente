import type { Metadata } from 'next'

export const metadata: Metadata = {
    title: 'Política de Privacidad | Pista Inteligente',
    description: 'Política de privacidad y uso de cookies para Pista Inteligente.',
    robots: {
        index: false,
        follow: true,
    }
}

export default function PrivacidadPage() {
    return (
        <div className="container" style={{ padding: '2rem 1rem', maxWidth: '800px', margin: '0 auto', color: 'var(--text-main)' }}>
            <h1 style={{ fontSize: '2rem', marginBottom: '1.5rem', fontWeight: 800 }}>Política de Privacidad</h1>

            <div className="glass-card" style={{ padding: '2rem' }}>
                <p style={{ marginBottom: '1rem' }}><strong>Última actualización:</strong> {new Date().toLocaleDateString('es-CL')}</p>

                <h2 style={{ fontSize: '1.5rem', marginTop: '1.5rem', marginBottom: '1rem', color: 'var(--secondary)' }}>1. Introducción</h2>
                <p style={{ marginBottom: '1rem', lineHeight: '1.6' }}>
                    En Pista Inteligente, valoramos tu privacidad. Esta política explica cómo recopilamos, usamos y protegemos tu información cuando visitas nuestro sitio web.
                </p>

                <h2 style={{ fontSize: '1.5rem', marginTop: '1.5rem', marginBottom: '1rem', color: 'var(--secondary)' }}>2. Publicidad y Cookies (Google AdSense)</h2>
                <p style={{ marginBottom: '1rem', lineHeight: '1.6' }}>
                    Utilizamos Google AdSense para mostrar anuncios. Google, como proveedor externo, utiliza cookies para mostrar anuncios en nuestro sitio.
                </p>
                <ul style={{ paddingLeft: '1.5rem', marginBottom: '1rem', lineHeight: '1.6' }}>
                    <li>Google utiliza la cookie DART que le permite mostrar anuncios a nuestros usuarios basándose en su visita a nuestro sitio y a otros sitios en Internet.</li>
                    <li>Los usuarios pueden inhabilitar el uso de la cookie DART visitando la <a href="https://policies.google.com/technologies/ads" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--primary)', textDecoration: 'underline' }}>política de privacidad de la red de contenido y anuncios de Google</a>.</li>
                </ul>

                <h2 style={{ fontSize: '1.5rem', marginTop: '1.5rem', marginBottom: '1rem', color: 'var(--secondary)' }}>3. Cookies de Terceros</h2>
                <p style={{ marginBottom: '1rem', lineHeight: '1.6' }}>
                    Nuestro sitio puede utilizar cookies de terceros para analizar el tráfico (como Vercel Analytics) y mejorar la experiencia del usuario. Estas cookies no recopilan información personal identificable.
                </p>

                <h2 style={{ fontSize: '1.5rem', marginTop: '1.5rem', marginBottom: '1rem', color: 'var(--secondary)' }}>4. Contacto</h2>
                <p style={{ marginBottom: '1rem', lineHeight: '1.6' }}>
                    Si tienes preguntas sobre esta política, puedes contactarnos a través de nuestros canales oficiales.
                </p>
            </div>
        </div>
    )
}
