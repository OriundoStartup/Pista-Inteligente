import type { Metadata } from 'next'

export const metadata: Metadata = {
    title: 'Términos y Condiciones - Pista Inteligente',
    description: 'Términos y Condiciones de uso de Pista Inteligente. Información legal sobre el uso de nuestras predicciones hípicas.',
}

export default function TerminosCondicionesPage() {
    return (
        <div className="container" style={{ padding: '2rem 0' }}>
            <article
                className="glass-card"
                style={{ maxWidth: '800px', margin: '0 auto', padding: '2rem' }}
            >
                <h1 style={{ marginBottom: '2rem', borderBottom: '1px solid rgba(255,255,255,0.2)', paddingBottom: '1rem' }}>
                    Términos y Condiciones de Uso
                </h1>

                <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>Última actualización: 18 de Diciembre de 2025</p>

                <p style={{ color: 'var(--text-muted)' }}>
                    Bienvenido a <strong>Pista Inteligente</strong>. Al acceder y utilizar nuestro sitio web, usted
                    acepta cumplir estos términos y condiciones de uso.
                </p>

                <h2 style={{ marginTop: '2rem', color: 'var(--secondary)' }}>1. Naturaleza del Servicio</h2>
                <p style={{ color: 'var(--text-muted)' }}>
                    Pista Inteligente proporciona análisis estadísticos y predicciones basadas en modelos de Inteligencia
                    Artificial para carreras hípicas en Chile. La información se ofrece únicamente con fines
                    <strong> informativos y de entretenimiento</strong>.
                </p>
                <p style={{ color: 'var(--accent)', fontWeight: 600 }}>
                    Descargo de responsabilidad: No garantizamos la exactitud de ninguna predicción.
                    Las apuestas implican riesgo financiero.
                </p>

                <h2 style={{ marginTop: '2rem', color: 'var(--primary)' }}>2. Propiedad Intelectual</h2>
                <p style={{ color: 'var(--text-muted)' }}>
                    Todo el contenido de este sitio es propiedad de <strong>MIND TRADING SPA</strong> y está protegido
                    por las leyes de propiedad intelectual de Chile.
                </p>

                <h2 style={{ marginTop: '2rem' }}>3. Uso Aceptable</h2>
                <ul style={{ color: 'var(--text-muted)', paddingLeft: '1.5rem' }}>
                    <li>No utilizar el sitio para fines ilegales.</li>
                    <li>No interferir con el funcionamiento del sitio (DDoS, scraping masivo).</li>
                    <li>No reproducir el servicio sin permiso expreso.</li>
                </ul>

                <h2 style={{ marginTop: '2rem' }}>4. Limitación de Responsabilidad</h2>
                <p style={{ color: 'var(--text-muted)' }}>
                    En ningún caso Pista Inteligente será responsable por daños directos, indirectos o consecuentes
                    que surjan del uso del servicio.
                </p>

                <h2 style={{ marginTop: '2rem' }}>5. Modificaciones</h2>
                <p style={{ color: 'var(--text-muted)' }}>
                    Nos reservamos el derecho de modificar estos términos en cualquier momento.
                </p>

                <h2 style={{ marginTop: '2rem' }}>6. Ley Aplicable</h2>
                <p style={{ color: 'var(--text-muted)' }}>
                    Estos términos se regirán por las leyes de la República de Chile.
                </p>

                <h2 style={{ marginTop: '2rem' }}>7. Contacto</h2>
                <p style={{ color: 'var(--text-muted)' }}>
                    Contáctenos en{' '}
                    <a href="https://oriundostartupchile.com" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--primary)' }}>
                        oriundostartupchile.com
                    </a>.
                </p>
            </article>
        </div>
    )
}
