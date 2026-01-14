import type { Metadata } from 'next'

export const metadata: Metadata = {
    title: 'Quiénes Somos - Pista Inteligente',
    description: 'Conozca al equipo detrás de Pista Inteligente. Expertos en Data Science e Inteligencia Artificial aplicados a la hípica.',
}

export default function QuienesSomosPage() {
    return (
        <div className="container" style={{ padding: '2rem 0' }}>
            <article
                className="glass-card"
                style={{ maxWidth: '800px', margin: '0 auto', padding: '2rem' }}
            >
                <h1 style={{ marginBottom: '2rem', borderBottom: '1px solid rgba(255,255,255,0.2)', paddingBottom: '1rem' }}>
                    Quiénes Somos
                </h1>

                <section style={{ marginBottom: '3rem' }}>
                    <h2 style={{ color: 'var(--secondary)' }}>Nuestra Misión</h2>
                    <p style={{ fontSize: '1.1rem', color: 'var(--text-muted)' }}>
                        Democratizar el acceso a datos deportivos de alta calidad mediante el uso ético y
                        transparente de la Inteligencia Artificial.
                    </p>
                    <p style={{ color: 'var(--text-muted)' }}>
                        En <strong>Pista Inteligente</strong>, combinamos la pasión por la hípica con la precisión de la
                        ciencia de datos. Nuestro objetivo es transformar la manera en que los aficionados y
                        profesionales analizan las carreras, proporcionando herramientas que van más allá de la
                        intuición, respaldadas por análisis estadísticos robustos.
                    </p>
                </section>

                <section style={{ marginBottom: '3rem' }}>
                    <h2 style={{ color: 'var(--primary)' }}>Tecnología e Innovación</h2>
                    <p style={{ color: 'var(--text-muted)' }}>
                        Somos parte del ecosistema de innovación de <strong>Oriundo Startup Chile</strong>. Nuestro
                        equipo de ingenieros y científicos de datos desarrolla modelos predictivos avanzados utilizando:
                    </p>
                    <ul style={{ color: 'var(--text-muted)', paddingLeft: '1.5rem' }}>
                        <li><strong>Machine Learning:</strong> Algoritmos de aprendizaje automático para identificar patrones complejos.</li>
                        <li><strong>Big Data:</strong> Procesamiento de miles de variables por carrera.</li>
                        <li><strong>Transparencia:</strong> Mostramos nuestras métricas de precisión públicamente.</li>
                    </ul>
                </section>

                <section style={{ marginBottom: '3rem' }}>
                    <h2 style={{ color: 'var(--accent)' }}>Nuestro Compromiso</h2>
                    <ul style={{ color: 'var(--text-muted)', paddingLeft: '1.5rem' }}>
                        <li><strong>Integridad:</strong> Datos veraces y sin sesgos manipulados.</li>
                        <li><strong>Responsabilidad:</strong> Promover el entretenimiento responsable e informado.</li>
                        <li><strong>Innovación Continua:</strong> Mejorar constantemente nuestros algoritmos.</li>
                    </ul>
                </section>

                <hr style={{ borderColor: 'rgba(255,255,255,0.1)', margin: '2rem 0' }} />

                <section>
                    <h3 style={{ color: 'var(--text-main)' }}>Contáctanos</h3>
                    <p style={{ color: 'var(--text-muted)' }}>
                        ¿Interesado en nuestra tecnología o tienes sugerencias para mejorar?
                    </p>
                    <p>
                        <a
                            href="https://oriundostartupchile.com"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="cta-button"
                            style={{ display: 'inline-block' }}
                        >
                            Visita oriundostartupchile.com
                        </a>
                    </p>
                </section>
            </article>
        </div>
    )
}
