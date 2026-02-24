import type { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
    title: 'Metodología de IA | Cómo Funciona Nuestro Modelo Predictivo | Pista Inteligente',
    description: 'Explicación técnica detallada del pipeline de Inteligencia Artificial de Pista Inteligente. Modelos LightGBM, XGBoost, CatBoost, feature engineering, calibración y validación.',
}

export default function MetodologiaPage() {
    return (
        <div className="container" style={{ padding: '2rem 0' }}>
            <article style={{ maxWidth: '800px', margin: '0 auto' }}>
                <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
                    <h1 style={{ fontSize: 'clamp(1.75rem, 5vw, 2.5rem)', color: 'var(--text-main)', marginBottom: '0.75rem', fontWeight: 800 }}>
                        🤖 Metodología de Inteligencia Artificial
                    </h1>
                    <p style={{ color: 'var(--text-muted)', fontSize: '1.05rem', maxWidth: '700px', margin: '0 auto', lineHeight: 1.7 }}>
                        Transparencia total sobre cómo funciona nuestro sistema predictivo. En esta página
                        explicamos en detalle cada etapa de nuestro pipeline de Machine Learning, desde la
                        recolección de datos hasta la publicación de las predicciones.
                    </p>
                </div>

                {/* Pipeline Overview */}
                <div className="glass-card" style={{ padding: '2rem', marginBottom: '1.5rem' }}>
                    <h2 style={{ color: 'var(--primary)', marginBottom: '1rem', fontSize: '1.4rem' }}>
                        📊 Visión General del Pipeline
                    </h2>
                    <p style={{ color: 'var(--text-muted)', lineHeight: 1.8, marginBottom: '1.25rem' }}>
                        Nuestro sistema de predicciones opera como un pipeline automatizado de extremo a extremo: desde la
                        recolección de datos de los hipódromos hasta la publicación de resultados en el frontend.
                        El proceso se ejecuta automáticamente cada vez que se detectan nuevos programas de carreras.
                    </p>

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '0.75rem', textAlign: 'center' }}>
                        {[
                            { step: '1', label: 'Scraping', icon: '📥', color: 'var(--secondary)' },
                            { step: '2', label: 'ETL', icon: '🔄', color: 'var(--primary)' },
                            { step: '3', label: 'Features', icon: '🧮', color: 'var(--accent)' },
                            { step: '4', label: 'Inferencia', icon: '🎯', color: '#FFD700' },
                            { step: '5', label: 'Publicación', icon: '📤', color: '#10b981' },
                        ].map((s) => (
                            <div key={s.step} style={{ padding: '1rem', background: 'rgba(255,255,255,0.03)', borderRadius: '12px', borderTop: `3px solid ${s.color}` }}>
                                <div style={{ fontSize: '1.5rem', marginBottom: '0.25rem' }}>{s.icon}</div>
                                <div style={{ color: s.color, fontWeight: 700, fontSize: '0.85rem' }}>{s.label}</div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Step 1: Data Collection */}
                <div className="glass-card" style={{ padding: '2rem', marginBottom: '1.5rem' }}>
                    <h2 style={{ color: 'var(--secondary)', marginBottom: '1rem', fontSize: '1.4rem' }}>
                        📥 Etapa 1: Recolección de Datos (Scraping)
                    </h2>
                    <p style={{ color: 'var(--text-muted)', lineHeight: 1.8, marginBottom: '1rem' }}>
                        El primer paso es obtener los datos. Nuestro sistema de scraping, desarrollado en Python con
                        BeautifulSoup y requests, monitorea automáticamente las páginas oficiales de los hipódromos
                        chilenos para detectar cuándo se publica un nuevo programa de carreras.
                    </p>
                    <p style={{ color: 'var(--text-muted)', lineHeight: 1.8, marginBottom: '1rem' }}>
                        Una vez detectado un programa, se extraen los datos de todos los partantes: nombre del caballo,
                        jinete, preparador, stud, haras, peso asignado, posición de partida, distancia de la carrera,
                        categoría y condición de pista. Además, recopilamos los <strong>resultados</strong> de cada jornada
                        una vez finalizada, incluyendo posiciones finales, tiempos y dividendos.
                    </p>
                    <p style={{ color: 'var(--text-muted)', lineHeight: 1.8 }}>
                        Estos datos se almacenan en una base de datos SQLite local para procesamiento rápido y posteriormente
                        se sincronizan con <strong>Supabase</strong> (PostgreSQL en la nube) para alimentar el frontend.
                    </p>
                </div>

                {/* Step 2: Feature Engineering */}
                <div className="glass-card" style={{ padding: '2rem', marginBottom: '1.5rem' }}>
                    <h2 style={{ color: 'var(--accent)', marginBottom: '1rem', fontSize: '1.4rem' }}>
                        🧮 Etapa 2: Ingeniería de Features
                    </h2>
                    <p style={{ color: 'var(--text-muted)', lineHeight: 1.8, marginBottom: '1.25rem' }}>
                        La calidad de las predicciones depende directamente de la calidad de las variables (features) que
                        alimentan al modelo. Nuestro pipeline genera más de 50 features por cada caballo participante,
                        agrupadas en las siguientes categorías:
                    </p>

                    <div style={{ display: 'grid', gap: '1rem' }}>
                        <div style={{ padding: '1.25rem', background: 'rgba(99, 102, 241, 0.06)', borderRadius: '8px', borderLeft: '3px solid var(--primary)' }}>
                            <h3 style={{ color: 'var(--primary)', fontSize: '1rem', marginBottom: '0.5rem' }}>Historial del Caballo</h3>
                            <p style={{ color: 'var(--text-muted)', margin: 0, lineHeight: 1.7, fontSize: '0.95rem' }}>
                                Win rate (porcentaje de victorias), place rate (top 2), show rate (top 3), tendencia de rendimiento
                                reciente (últimas 3-5 carreras), rendimiento en la distancia específica, rendimiento en el hipódromo
                                específico y categoría relativa.
                            </p>
                        </div>
                        <div style={{ padding: '1.25rem', background: 'rgba(52, 211, 153, 0.06)', borderRadius: '8px', borderLeft: '3px solid var(--secondary)' }}>
                            <h3 style={{ color: 'var(--secondary)', fontSize: '1rem', marginBottom: '0.5rem' }}>Rendimiento del Jinete</h3>
                            <p style={{ color: 'var(--text-muted)', margin: 0, lineHeight: 1.7, fontSize: '0.95rem' }}>
                                Eficiencia general del jinete, eficiencia rolling (últimos 30/60/90 días), rendimiento en el hipódromo
                                específico, y un feature de interacción jinete-caballo que mide el historial de la combinación específica.
                            </p>
                        </div>
                        <div style={{ padding: '1.25rem', background: 'rgba(251, 191, 36, 0.06)', borderRadius: '8px', borderLeft: '3px solid var(--accent)' }}>
                            <h3 style={{ color: 'var(--accent)', fontSize: '1rem', marginBottom: '0.5rem' }}>Factores de Carrera</h3>
                            <p style={{ color: 'var(--text-muted)', margin: 0, lineHeight: 1.7, fontSize: '0.95rem' }}>
                                Posición de partida (riel interior vs exterior), peso asignado, días de descanso desde la última carrera,
                                categoría de la carrera, distancia, y análisis de los rivales directos (fuerza del campo).
                            </p>
                        </div>
                        <div style={{ padding: '1.25rem', background: 'rgba(255, 215, 0, 0.06)', borderRadius: '8px', borderLeft: '3px solid #FFD700' }}>
                            <h3 style={{ color: '#FFD700', fontSize: '1rem', marginBottom: '0.5rem' }}>Features Categóricos</h3>
                            <p style={{ color: 'var(--text-muted)', margin: 0, lineHeight: 1.7, fontSize: '0.95rem' }}>
                                Preparador (entrenador), stud (propietario), haras de origen. Estos features se procesan mediante
                                Target Encoding, que asigna a cada categoría el rendimiento promedio histórico observado.
                            </p>
                        </div>
                    </div>
                </div>

                {/* Step 3: Model Architecture */}
                <div className="glass-card" style={{ padding: '2rem', marginBottom: '1.5rem' }}>
                    <h2 style={{ color: 'var(--primary)', marginBottom: '1rem', fontSize: '1.4rem' }}>
                        🏗️ Etapa 3: Arquitectura del Modelo (Ensemble)
                    </h2>
                    <p style={{ color: 'var(--text-muted)', lineHeight: 1.8, marginBottom: '1.25rem' }}>
                        Utilizamos una arquitectura de <strong>Stacking Ensemble</strong> que combina tres modelos base
                        de Gradient Boosting con un meta-learner. La idea central es que cada modelo comete errores
                        diferentes, y al combinarlos, los errores individuales se compensan.
                    </p>

                    <div style={{ display: 'grid', gap: '1rem', marginBottom: '1.25rem' }}>
                        <div style={{ padding: '1rem', background: 'rgba(255,255,255,0.03)', borderRadius: '8px' }}>
                            <h3 style={{ color: 'var(--primary)', fontSize: '1rem', marginBottom: '0.5rem' }}>🔵 LightGBM (Modelo Principal)</h3>
                            <p style={{ color: 'var(--text-muted)', margin: 0, lineHeight: 1.7, fontSize: '0.95rem' }}>
                                Gradient Boosting optimizado para velocidad, usando crecimiento de árbol basado en histogramas.
                                Es el modelo más rápido de entrenar y ofrece un excelente balance entre velocidad y precisión.
                                Configurado con objetivo de ranking (LambdaRank) para optimizar directamente el orden de los caballos.
                            </p>
                        </div>
                        <div style={{ padding: '1rem', background: 'rgba(255,255,255,0.03)', borderRadius: '8px' }}>
                            <h3 style={{ color: 'var(--secondary)', fontSize: '1rem', marginBottom: '0.5rem' }}>🟢 XGBoost (Modelo Secundario)</h3>
                            <p style={{ color: 'var(--text-muted)', margin: 0, lineHeight: 1.7, fontSize: '0.95rem' }}>
                                Extreme Gradient Boosting con regularización L1 y L2 para prevenir sobreajuste.
                                Aporta robustez al ensemble gracias a su control avanzado de complejidad del modelo.
                                Especialmente útil cuando los datos tienen ruido o patrones espurios.
                            </p>
                        </div>
                        <div style={{ padding: '1rem', background: 'rgba(255,255,255,0.03)', borderRadius: '8px' }}>
                            <h3 style={{ color: 'var(--accent)', fontSize: '1rem', marginBottom: '0.5rem' }}>🟡 CatBoost (Modelo Terciario)</h3>
                            <p style={{ color: 'var(--text-muted)', margin: 0, lineHeight: 1.7, fontSize: '0.95rem' }}>
                                Gradient Boosting especializado en variables categóricas de alta cardinalidad (como el nombre
                                del jinete, preparador o haras). Implementa Target Statistics para encoding categórico nativo,
                                sin necesidad de preprocesamiento manual, lo que reduce el riesgo de data leakage.
                            </p>
                        </div>
                        <div style={{ padding: '1rem', background: 'rgba(255, 215, 0, 0.08)', borderRadius: '8px', border: '1px solid rgba(255, 215, 0, 0.2)' }}>
                            <h3 style={{ color: '#FFD700', fontSize: '1rem', marginBottom: '0.5rem' }}>⚡ Meta-Learner: Ridge Regression</h3>
                            <p style={{ color: 'var(--text-muted)', margin: 0, lineHeight: 1.7, fontSize: '0.95rem' }}>
                                Las predicciones de los tres modelos base se combinan usando Ridge Regression (regresión lineal
                                con regularización L2). Este meta-learner aprende cuánto peso asignar a cada modelo base según
                                su rendimiento histórico, generando una predicción final más estable que cualquier modelo individual.
                            </p>
                        </div>
                    </div>
                </div>

                {/* Step 4: Calibration */}
                <div className="glass-card" style={{ padding: '2rem', marginBottom: '1.5rem' }}>
                    <h2 style={{ color: 'var(--secondary)', marginBottom: '1rem', fontSize: '1.4rem' }}>
                        📐 Etapa 4: Calibración de Probabilidades
                    </h2>
                    <p style={{ color: 'var(--text-muted)', lineHeight: 1.8, marginBottom: '1rem' }}>
                        Los modelos de Gradient Boosting generan scores que no necesariamente representan probabilidades
                        bien calibradas. Por ejemplo, un score de 0.70 no significa necesariamente que el caballo tenga
                        70% de probabilidad de ganar.
                    </p>
                    <p style={{ color: 'var(--text-muted)', lineHeight: 1.8, marginBottom: '1rem' }}>
                        Para resolver esto, aplicamos <strong>Isotonic Regression</strong> como paso de post-procesamiento.
                        Este calibrador no-paramétrico ajusta las probabilidades para que reflejen la frecuencia real de
                        aciertos observada en datos históricos. Si el calibrador dice 0.30, significa que históricamente,
                        los caballos con ese score aproximado han ganado aproximadamente el 30% de las veces.
                    </p>
                    <p style={{ color: 'var(--text-muted)', lineHeight: 1.8 }}>
                        La calibración es especialmente importante para que el <strong>Score de Confianza</strong> mostrado
                        en las predicciones sea interpretable y no engañoso. Un score calibrado permite al usuario
                        comparar directamente las probabilidades entre caballos de la misma carrera.
                    </p>
                </div>

                {/* Step 5: Validation */}
                <div className="glass-card" style={{ padding: '2rem', marginBottom: '1.5rem' }}>
                    <h2 style={{ color: 'var(--accent)', marginBottom: '1rem', fontSize: '1.4rem' }}>
                        ✅ Etapa 5: Validación y Monitoreo
                    </h2>
                    <p style={{ color: 'var(--text-muted)', lineHeight: 1.8, marginBottom: '1rem' }}>
                        No basta con entrenar un modelo una vez; es necesario monitorear continuamente su rendimiento
                        para detectar degradación. Nuestro sistema implementa:
                    </p>
                    <ul style={{ color: 'var(--text-muted)', paddingLeft: '1.5rem', lineHeight: 1.8, marginBottom: '1rem' }}>
                        <li>
                            <strong>Validación temporal:</strong> Usamos los datos más recientes como conjunto de validación
                            (time-series split), nunca datos aleatorios, para simular condiciones reales de predicción.
                        </li>
                        <li>
                            <strong>Métricas de rendimiento:</strong> Tasa de acierto para ganador exacto, quiniela (top 2),
                            trifecta (top 3) y superfecta (top 4), calculadas y publicadas automáticamente.
                        </li>
                        <li>
                            <strong>Monitoreo de drift:</strong> Un script de detección de drift usando PSI (Population Stability Index)
                            alerta si la distribución de los datos de entrada cambia significativamente, lo que podría indicar
                            que el modelo necesita reentrenamiento.
                        </li>
                        <li>
                            <strong>Transparencia:</strong> Todas las métricas de rendimiento se muestran públicamente en la{' '}
                            <Link href="/precision" style={{ color: 'var(--primary)', textDecoration: 'underline' }}>página de Precisión</Link>.
                        </li>
                    </ul>
                </div>

                {/* Limitations */}
                <div className="glass-card" style={{ padding: '2rem', marginBottom: '1.5rem', borderLeft: '4px solid var(--accent)' }}>
                    <h2 style={{ color: 'var(--accent)', marginBottom: '1rem', fontSize: '1.4rem' }}>
                        ⚠️ Limitaciones del Modelo
                    </h2>
                    <p style={{ color: 'var(--text-muted)', lineHeight: 1.8, marginBottom: '1rem' }}>
                        En aras de la transparencia total, es importante mencionar las limitaciones conocidas de nuestro sistema:
                    </p>
                    <ul style={{ color: 'var(--text-muted)', paddingLeft: '1.5rem', lineHeight: 1.8 }}>
                        <li>
                            <strong>Caballos debutantes:</strong> Para caballos sin historial de carreras, el modelo tiene información
                            limitada y depende más del preparador, jinete y haras de origen.
                        </li>
                        <li>
                            <strong>Eventos atípicos:</strong> Incidentes durante la carrera (tropezones, interferencias, salidas falsas)
                            son inherentemente impredecibles.
                        </li>
                        <li>
                            <strong>Cambios de último minuto:</strong> Sustituciones de jinete o retiros de último momento pueden
                            afectar la precisión si ocurren después de la generación de predicciones.
                        </li>
                        <li>
                            <strong>Sesgo de datos:</strong> El modelo puede estar sesgado hacia patrones del pasado reciente,
                            lo que mitigamos con monitoreo de drift y reentrenamiento periódico.
                        </li>
                    </ul>
                </div>

                {/* CTA */}
                <div style={{ textAlign: 'center', padding: '2rem 1rem', background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(52, 211, 153, 0.1))', borderRadius: '16px' }}>
                    <h2 style={{ color: 'var(--text-main)', marginBottom: '1rem', fontSize: 'clamp(1.25rem, 4vw, 1.75rem)' }}>
                        ¿Quieres ver el modelo en acción?
                    </h2>
                    <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
                        <Link href="/programa" className="cta-button" style={{ display: 'inline-block' }}>
                            Ver Predicciones de Hoy
                        </Link>
                        <Link href="/precision" style={{ display: 'inline-block', padding: '1rem 2rem', border: '1px solid var(--primary)', borderRadius: '50px', color: 'var(--primary)', textDecoration: 'none', fontWeight: 600 }}>
                            Rendimiento Verificado
                        </Link>
                    </div>
                </div>
            </article>
        </div>
    )
}
