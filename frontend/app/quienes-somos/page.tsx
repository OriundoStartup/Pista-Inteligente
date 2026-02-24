import type { Metadata } from 'next'

export const metadata: Metadata = {
    title: 'Quiénes Somos - Pista Inteligente | Equipo y Metodología',
    description: 'Conozca al equipo detrás de Pista Inteligente. Expertos en Data Science e Inteligencia Artificial aplicados a la hípica chilena. Parte de Oriundo Startup Chile.',
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

                <section style={{ marginBottom: '2.5rem' }}>
                    <h2 style={{ color: 'var(--secondary)' }}>Nuestra Misión</h2>
                    <p style={{ fontSize: '1.1rem', color: 'var(--text-muted)', lineHeight: 1.7 }}>
                        Democratizar el acceso a datos deportivos de alta calidad mediante el uso ético y
                        transparente de la Inteligencia Artificial.
                    </p>
                    <p style={{ color: 'var(--text-muted)', lineHeight: 1.7 }}>
                        En <strong>Pista Inteligente</strong>, combinamos la pasión por la hípica con la precisión de la
                        ciencia de datos. Nuestro objetivo es transformar la manera en que los aficionados y
                        profesionales analizan las carreras de caballos en Chile, proporcionando herramientas que van más allá de la
                        intuición, respaldadas por análisis estadísticos robustos con datos reales.
                    </p>
                    <p style={{ color: 'var(--text-muted)', lineHeight: 1.7 }}>
                        Creemos que la información de calidad no debería ser exclusiva de unos pocos. Por eso ofrecemos
                        nuestras predicciones de forma gratuita y mostramos públicamente nuestras métricas de rendimiento,
                        para que cada usuario pueda evaluar por sí mismo la utilidad de nuestro sistema.
                    </p>
                </section>

                <section style={{ marginBottom: '2.5rem' }}>
                    <h2 style={{ color: 'var(--primary)' }}>Nuestra Historia</h2>
                    <p style={{ color: 'var(--text-muted)', lineHeight: 1.7 }}>
                        Pista Inteligente nació como un proyecto de <strong>Oriundo Startup Chile SpA</strong>, una startup
                        tecnológica enfocada en aplicar técnicas de Machine Learning a dominios deportivos. La idea surgió
                        al observar que el análisis hípico tradicional en Chile dependía mayoritariamente de la experiencia
                        subjetiva, sin aprovechar el potencial de los datos históricos disponibles.
                    </p>
                    <p style={{ color: 'var(--text-muted)', lineHeight: 1.7 }}>
                        Comenzamos recopilando datos de carreras chilenas y construyendo modelos predictivos simples.
                        A medida que acumulamos más datos y refinamos nuestras técnicas, evolucionamos hacia un ensemble
                        de tres modelos de Gradient Boosting (LightGBM, XGBoost y CatBoost) con calibración isotónica,
                        logrando predicciones cada vez más precisas.
                    </p>
                    <p style={{ color: 'var(--text-muted)', lineHeight: 1.7 }}>
                        Hoy cubrimos los cuatro principales hipódromos del país: Hipódromo Chile, Club Hípico de Santiago,
                        Valparaíso Sporting y Club Hípico de Concepción, procesando automáticamente cada programa de carreras
                        y publicando predicciones antes de cada jornada.
                    </p>
                </section>

                <section style={{ marginBottom: '2.5rem' }}>
                    <h2 style={{ color: 'var(--primary)' }}>Tecnología e Innovación</h2>
                    <p style={{ color: 'var(--text-muted)', lineHeight: 1.7 }}>
                        Somos parte del ecosistema de innovación de <strong>Oriundo Startup Chile</strong>. Nuestro
                        equipo de ingenieros y científicos de datos desarrolla modelos predictivos avanzados utilizando:
                    </p>
                    <ul style={{ color: 'var(--text-muted)', paddingLeft: '1.5rem', lineHeight: 1.8 }}>
                        <li>
                            <strong>Machine Learning Ensemble:</strong> Tres modelos de Gradient Boosting (LightGBM, XGBoost, CatBoost)
                            combinados mediante un meta-learner de Ridge Regression para máxima robustez.
                        </li>
                        <li>
                            <strong>Feature Engineering Avanzado:</strong> Más de 50 variables predictivas incluyendo estadísticas rolling,
                            interacciones jinete-caballo, factores de pista y tendencias temporales.
                        </li>
                        <li>
                            <strong>Calibración de Probabilidades:</strong> Isotonic Regression para asegurar que las probabilidades
                            generadas reflejen la frecuencia real de aciertos observada.
                        </li>
                        <li>
                            <strong>Pipeline Automatizado:</strong> Recolección de datos, procesamiento, predicción y publicación
                            ejecutados automáticamente sin intervención manual.
                        </li>
                        <li>
                            <strong>Transparencia:</strong> Mostramos nuestras métricas de precisión públicamente en la página de
                            rendimiento, sin manipulaciones.
                        </li>
                    </ul>
                </section>

                <section style={{ marginBottom: '2.5rem' }}>
                    <h2 style={{ color: 'var(--accent)' }}>Nuestro Compromiso</h2>
                    <ul style={{ color: 'var(--text-muted)', paddingLeft: '1.5rem', lineHeight: 1.8 }}>
                        <li>
                            <strong>Integridad:</strong> Datos veraces y sin sesgos manipulados. Cada predicción se registra
                            antes de la carrera y se compara con resultados oficiales.
                        </li>
                        <li>
                            <strong>Responsabilidad:</strong> Promover el entretenimiento responsable e informado. No incentivamos
                            las apuestas, sino el análisis deportivo basado en datos.
                        </li>
                        <li>
                            <strong>Innovación Continua:</strong> Mejorar constantemente nuestros algoritmos incorporando nuevos
                            datos, features y técnicas de modelado.
                        </li>
                        <li>
                            <strong>Acceso Gratuito:</strong> Mantenemos el acceso libre a las predicciones para democratizar
                            la información hípica de calidad.
                        </li>
                    </ul>
                </section>

                <section style={{ marginBottom: '2.5rem' }}>
                    <h2 style={{ color: 'var(--text-main)' }}>Stack Tecnológico</h2>
                    <p style={{ color: 'var(--text-muted)', lineHeight: 1.7 }}>
                        Nuestra plataforma está construida con tecnologías modernas orientadas al rendimiento y la escalabilidad:
                    </p>
                    <ul style={{ color: 'var(--text-muted)', paddingLeft: '1.5rem', lineHeight: 1.8 }}>
                        <li><strong>Frontend:</strong> Next.js con Server-Side Rendering para SEO y velocidad de carga óptima.</li>
                        <li><strong>Backend de Datos:</strong> Python con pandas, scikit-learn, LightGBM, XGBoost y CatBoost.</li>
                        <li><strong>Base de Datos:</strong> Supabase (PostgreSQL) con Row-Level Security para protección de datos.</li>
                        <li><strong>Infraestructura:</strong> Vercel para el frontend, Cloud Run para procesos de ML.</li>
                        <li><strong>Automatización:</strong> GitHub Actions para CI/CD y sincronización de datos programada.</li>
                    </ul>
                </section>

                <hr style={{ borderColor: 'rgba(255,255,255,0.1)', margin: '2rem 0' }} />

                <section>
                    <h3 style={{ color: 'var(--text-main)' }}>Contáctanos</h3>
                    <p style={{ color: 'var(--text-muted)', lineHeight: 1.7 }}>
                        ¿Interesado en nuestra tecnología, tienes sugerencias para mejorar o quieres reportar un error?
                        Estamos abiertos a recibir feedback de la comunidad hípica.
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
