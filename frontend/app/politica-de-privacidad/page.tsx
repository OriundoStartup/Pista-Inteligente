import type { Metadata } from 'next'

export const metadata: Metadata = {
    title: 'Política de Privacidad - Pista Inteligente',
    description: 'Política de Privacidad de Pista Inteligente. Conoce cómo recopilamos, usamos y protegemos tus datos personales.',
}

export default function PoliticaPrivacidadPage() {
    return (
        <div className="container" style={{ padding: '2rem 0' }}>
            <article
                className="glass-card"
                style={{ maxWidth: '800px', margin: '0 auto', padding: '2rem' }}
            >
                <h1 style={{ marginBottom: '2rem', borderBottom: '1px solid rgba(255,255,255,0.2)', paddingBottom: '1rem' }}>
                    Política de Privacidad
                </h1>

                <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>Última actualización: 18 de Diciembre de 2025</p>

                <p style={{ color: 'var(--text-muted)' }}>
                    En <strong>Pista Inteligente</strong>, valoramos y respetamos su privacidad. Esta Política de
                    Privacidad describe cómo recopilamos, utilizamos y protegemos la información personal.
                </p>

                <h2 style={{ marginTop: '2rem', color: 'var(--secondary)' }}>1. Información que Recopilamos</h2>
                <ul style={{ color: 'var(--text-muted)', paddingLeft: '1.5rem' }}>
                    <li><strong>Datos de Navegación:</strong> Información sobre su dispositivo, dirección IP, tipo de navegador, páginas visitadas.</li>
                    <li><strong>Interacciones con el Chatbot:</strong> Las consultas realizadas a nuestro asistente de IA.</li>
                </ul>

                <h2 style={{ marginTop: '2rem', color: 'var(--primary)' }}>2. Uso de la Información</h2>
                <ul style={{ color: 'var(--text-muted)', paddingLeft: '1.5rem' }}>
                    <li>Proporcionar y mantener nuestros servicios de predicción hípica.</li>
                    <li>Mejorar la funcionalidad y el rendimiento del sitio web.</li>
                    <li>Analizar tendencias de uso para optimizar nuestros modelos de IA.</li>
                    <li>Mostrar publicidad relevante a través de Google AdSense.</li>
                </ul>

                <h2 style={{ marginTop: '2rem', color: 'var(--accent)' }}>3. Cookies y Tecnologías de Terceros</h2>
                <ul style={{ color: 'var(--text-muted)', paddingLeft: '1.5rem' }}>
                    <li><strong>Google Analytics:</strong> Para análisis de tráfico y comportamiento.</li>
                    <li><strong>Google AdSense:</strong> Para servir anuncios publicitarios.</li>
                </ul>

                <h2 style={{ marginTop: '2rem' }}>4. Protección de Datos</h2>
                <p style={{ color: 'var(--text-muted)' }}>
                    Implementamos medidas de seguridad razonables para proteger su información contra el acceso no autorizado.
                </p>

                <h2 style={{ marginTop: '2rem' }}>5. Enlaces a Terceros</h2>
                <p style={{ color: 'var(--text-muted)' }}>
                    Nuestro sitio puede contener enlaces a sitios web externos. No somos responsables de sus prácticas de privacidad.
                </p>

                <h2 style={{ marginTop: '2rem' }}>6. Cambios en esta Política</h2>
                <p style={{ color: 'var(--text-muted)' }}>
                    Nos reservamos el derecho de actualizar esta Política en cualquier momento.
                </p>

                <h2 style={{ marginTop: '2rem' }}>7. Contacto</h2>
                <p style={{ color: 'var(--text-muted)' }}>
                    Si tiene preguntas, contáctenos a través de{' '}
                    <a href="https://oriundostartupchile.com" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--primary)' }}>
                        oriundostartupchile.com
                    </a>.
                </p>
            </article>
        </div>
    )
}
