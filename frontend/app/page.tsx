import { createClient } from '@supabase/supabase-js'
import Link from 'next/link'
import JackpotAlert from '@/components/JackpotAlert'

// ISR: Revalidar cada 5 minutos
export const revalidate = 300

// Fetch stats from Supabase (real data only)
async function getStats() {
  const supabase = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!)
  try {
    // Get total races count
    const { count: totalCarreras } = await supabase
      .from('carreras')
      .select('*', { count: 'exact', head: true })

    // Get predictions count
    const { count: totalPredicciones } = await supabase
      .from('predicciones')
      .select('*', { count: 'exact', head: true })

    // Get total hipódromos
    const { count: totalHipodromos } = await supabase
      .from('hipodromos')
      .select('*', { count: 'exact', head: true })

    return {
      total_carreras: totalCarreras || 0,
      total_predicciones: totalPredicciones || 0,
      total_hipodromos: totalHipodromos || 0
    }
  } catch {
    return {
      total_carreras: 0,
      total_predicciones: 0,
      total_hipodromos: 0
    }
  }
}

interface JineteStat {
  jinete: string
  ganadas: number
  eficiencia: string
}

// Fetch top jockeys using Database Function (RPC) for performance and complete data
async function getTopJinetes(): Promise<JineteStat[]> {
  const supabase = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!)
  try {
    // 1. Try RPC Call (Server-side aggregation)
    const { data, error } = await supabase.rpc('get_top_jinetes_2026')

    if (error) {
      console.warn("RPC get_top_jinetes_2026 failed, falling back to legacy fetch:", error.message)
      return getTopJinetesLegacy(supabase)
    }

    if (!data || data.length === 0) {
      console.log("No data from RPC")
      return getTopJinetesLegacy(supabase)
    }

    // Map RPC result
    return data.map((j: any) => ({
      jinete: j.jinete,
      ganadas: Number(j.ganadas),
      eficiencia: j.eficiencia // Already formatted as text in SQL
    }))

  } catch (e) {
    console.error("Exception in getTopJinetes:", e)
    return fallbackJinetes()
  }
}

// Legacy method (Client-side aggregation) - Subject to 1000 row limit
async function getTopJinetesLegacy(supabase: any): Promise<JineteStat[]> {
  try {
    // Fetch all participaciones with jornada dates from 2026
    const { data, error } = await supabase
      .from('participaciones')
      .select(`
        posicion,
        jinetes (nombre),
        carreras!inner (
          jornadas!inner (
            fecha
          )
        )
      `)
      .gte('carreras.jornadas.fecha', '2026-01-01')
      .lte('carreras.jornadas.fecha', '2026-12-31')

    if (error) {
      console.error("Error fetching jinetes 2026 (Legacy):", error)
      return fallbackJinetes()
    }

    if (!data || data.length === 0) {
      return fallbackJinetes()
    }

    // Aggregate wins and mounts
    const stats: Record<string, { ganadas: number; montes: number }> = {}

    data.forEach((row: any) => {
      const jineteName = row.jinetes?.nombre || 'Desconocido'
      const nombre = jineteName.trim()

      if (!stats[nombre]) {
        stats[nombre] = { ganadas: 0, montes: 0 }
      }

      stats[nombre].montes += 1

      // Count wins (position 1)
      if (row.posicion == 1 || row.posicion == '1') {
        stats[nombre].ganadas += 1
      }
    })

    // Convert to array and sort by wins
    const sortedJinetes = Object.entries(stats)
      .map(([nombre, stat]) => ({
        jinete: nombre,
        ganadas: stat.ganadas,
        eficiencia: stat.montes > 0 ? ((stat.ganadas / stat.montes) * 100).toFixed(1) : '0.0'
      }))
      .sort((a, b) => b.ganadas - a.ganadas)
      .slice(0, 5)

    return sortedJinetes.length > 0 ? sortedJinetes : fallbackJinetes()

  } catch (e) {
    console.error("Exception in getTopJinetesLegacy:", e)
    return fallbackJinetes()
  }
}

function fallbackJinetes(): JineteStat[] {
  return [
    { jinete: 'J. Medina', ganadas: 0, eficiencia: '0.0' },
    { jinete: 'B. Sancho', ganadas: 0, eficiencia: '0.0' },
    { jinete: 'Sin Datos', ganadas: 0, eficiencia: '0.0' },
  ]
}

export default async function Home() {
  const stats = await getStats()
  const topJinetes = await getTopJinetes()

  return (
    <>
      {/* Hero Section - SEO Optimized */}
      <section className="hero" itemScope itemType="https://schema.org/WebPage">
        <h1 itemProp="name">
          Predicciones Hípicas con IA para Chile<br />
          Hipódromo Chile, Santiago, Valparaíso y Concepción
        </h1>
        <p itemProp="description">
          Utilizamos algoritmos de última generación para analizar el{' '}
          <strong>Programa del Hipódromo Chile</strong>, las carreras del{' '}
          <strong>Club Hípico de Santiago</strong>, <strong>Valparaíso Sporting</strong> y <strong>Club Hípico de Concepción</strong>.
          Detectamos patrones ocultos en miles de resultados históricos para entregarte
          <strong> pronósticos profesionales</strong> con las mejores probabilidades de acierto.
        </p>
        <p style={{ fontSize: '0.95rem', opacity: 0.9, marginTop: '0.5rem' }}>
          🏇 Programa del día • Resultados en vivo • Estadísticas de jinetes • Análisis de carreras
        </p>
        <Link href="/programa" className="cta-button">
          Ver Programa de Hoy con Predicciones IA
        </Link>
      </section>

      {/* Stats Card - Real data only */}
      <div className="glass-card">
        <div className="section-title">📊 Nuestra Base de Datos</div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '0.75rem' }}>
          <div style={{ textAlign: 'center', padding: '1rem' }}>
            <span
              className="stat-number"
              style={{ fontSize: 'clamp(1.8rem, 5vw, 3rem)', color: 'var(--secondary)', display: 'block', fontWeight: 800 }}
            >
              {stats.total_carreras.toLocaleString()}
            </span>
            <p style={{ fontSize: '0.9rem' }}>Carreras Analizadas</p>
          </div>
          <div style={{ textAlign: 'center', padding: '1rem' }}>
            <span
              className="stat-number"
              style={{ fontSize: 'clamp(1.8rem, 5vw, 3rem)', color: 'var(--primary)', display: 'block', fontWeight: 800 }}
            >
              {stats.total_predicciones.toLocaleString()}
            </span>
            <p style={{ fontSize: '0.9rem' }}>Predicciones Generadas</p>
          </div>
          <div style={{ textAlign: 'center', padding: '1rem' }}>
            <span
              className="stat-number"
              style={{ fontSize: 'clamp(1.8rem, 5vw, 3rem)', color: 'var(--accent)', display: 'block', fontWeight: 800 }}
            >
              {stats.total_hipodromos}
            </span>
            <p style={{ fontSize: '0.9rem' }}>Hipódromos Cubiertos</p>
          </div>
        </div>
      </div>

      {/* How It Works - Original educational content */}
      <div className="glass-card" style={{ marginTop: '1.5rem' }}>
        <div className="section-title">🤖 ¿Cómo Funciona Pista Inteligente?</div>
        <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem', lineHeight: 1.7, fontSize: '1rem' }}>
          Pista Inteligente utiliza un <strong>ensemble de tres modelos de Machine Learning</strong> (LightGBM, XGBoost y CatBoost)
          combinados mediante un meta-learner de Ridge Regression. Nuestro sistema procesa más de 50 variables por cada caballo
          participante, incluyendo historial de rendimiento, condición de pista, descanso entre carreras, combinación jinete-caballo
          y tendencias recientes. A continuación, un resumen del proceso:
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem' }}>
          <div style={{ textAlign: 'center', padding: '1.5rem', background: 'rgba(99, 102, 241, 0.08)', borderRadius: '12px' }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>📥</div>
            <h3 style={{ color: 'var(--primary)', marginBottom: '0.5rem', fontSize: '1.1rem' }}>1. Recolección de Datos</h3>
            <p style={{ color: 'var(--text-muted)', margin: 0, fontSize: '0.95rem', lineHeight: 1.6 }}>
              Cada día recopilamos automáticamente los programas de carreras publicados por los hipódromos oficiales de Chile.
              Extraemos información de partantes, jinetes, preparadores, distancias, pesos y condiciones de pista.
            </p>
          </div>
          <div style={{ textAlign: 'center', padding: '1.5rem', background: 'rgba(52, 211, 153, 0.08)', borderRadius: '12px' }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>🧮</div>
            <h3 style={{ color: 'var(--secondary)', marginBottom: '0.5rem', fontSize: '1.1rem' }}>2. Ingeniería de Features</h3>
            <p style={{ color: 'var(--text-muted)', margin: 0, fontSize: '0.95rem', lineHeight: 1.6 }}>
              Transformamos los datos crudos en más de 50 variables predictivas: eficiencia del jinete, tendencia del caballo,
              ventaja por posición de partida, factor de descanso óptimo, historial en la distancia específica y más.
            </p>
          </div>
          <div style={{ textAlign: 'center', padding: '1.5rem', background: 'rgba(251, 191, 36, 0.08)', borderRadius: '12px' }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>🎯</div>
            <h3 style={{ color: 'var(--accent)', marginBottom: '0.5rem', fontSize: '1.1rem' }}>3. Predicción con IA</h3>
            <p style={{ color: 'var(--text-muted)', margin: 0, fontSize: '0.95rem', lineHeight: 1.6 }}>
              Nuestro ensemble de modelos genera un <strong>Score de Confianza</strong> calibrado para cada caballo.
              Los resultados se publican antes de cada jornada hípica. Puedes verificar nuestra precisión real en la{' '}
              <Link href="/precision" style={{ color: 'var(--primary)', textDecoration: 'underline' }}>página de rendimiento</Link>.
            </p>
          </div>
        </div>
      </div>

      {/* Top Jinetes Card */}
      <div className="glass-card" style={{ marginTop: '1.5rem' }}>
        <div className="section-title">🏆 Top Jinetes 2026 (En Vivo)</div>
        <p style={{ color: 'var(--text-muted)', marginBottom: '1rem', fontSize: '0.95rem', lineHeight: 1.6 }}>
          Ranking actualizado automáticamente con datos de todas las carreras disputadas en 2026 en los hipódromos de Chile.
          La eficiencia mide el porcentaje de victorias sobre el total de montas de cada jinete.
        </p>
        <table className="modern-table">
          <thead>
            <tr>
              <th>Jinete</th>
              <th>Triunfos</th>
              <th>Eficiencia</th>
            </tr>
          </thead>
          <tbody>
            {topJinetes.map((jinete, index) => (
              <tr key={index}>
                <td>{jinete.jinete}</td>
                <td>{jinete.ganadas}</td>
                <td>{jinete.eficiencia}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* FAQ Section - Structured data for SEO */}
      <div className="glass-card" style={{ marginTop: '1.5rem' }}>
        <div className="section-title">❓ Preguntas Frecuentes</div>

        <div itemScope itemType="https://schema.org/FAQPage">
          <div itemScope itemProp="mainEntity" itemType="https://schema.org/Question" style={{ marginBottom: '1.5rem', padding: '1.25rem', background: 'rgba(255,255,255,0.03)', borderRadius: '12px', borderLeft: '3px solid var(--primary)' }}>
            <h3 itemProp="name" style={{ color: 'var(--text-main)', fontSize: '1.05rem', marginBottom: '0.5rem', fontWeight: 700 }}>
              ¿Qué es Pista Inteligente y cómo genera sus predicciones?
            </h3>
            <div itemScope itemProp="acceptedAnswer" itemType="https://schema.org/Answer">
              <p itemProp="text" style={{ color: 'var(--text-muted)', margin: 0, lineHeight: 1.7, fontSize: '0.95rem' }}>
                Pista Inteligente es una plataforma chilena de análisis hípico que utiliza Inteligencia Artificial para
                generar predicciones de carreras de caballos. Nuestro sistema emplea un ensemble de tres modelos de Machine Learning
                (LightGBM, XGBoost y CatBoost) que analizan más de 50 variables por participante, incluyendo historial del caballo,
                rendimiento del jinete, condición de pista y patrones estadísticos. Las predicciones se publican antes de cada jornada.
              </p>
            </div>
          </div>

          <div itemScope itemProp="mainEntity" itemType="https://schema.org/Question" style={{ marginBottom: '1.5rem', padding: '1.25rem', background: 'rgba(255,255,255,0.03)', borderRadius: '12px', borderLeft: '3px solid var(--secondary)' }}>
            <h3 itemProp="name" style={{ color: 'var(--text-main)', fontSize: '1.05rem', marginBottom: '0.5rem', fontWeight: 700 }}>
              ¿Qué hipódromos cubre Pista Inteligente?
            </h3>
            <div itemScope itemProp="acceptedAnswer" itemType="https://schema.org/Answer">
              <p itemProp="text" style={{ color: 'var(--text-muted)', margin: 0, lineHeight: 1.7, fontSize: '0.95rem' }}>
                Cubrimos los cuatro principales hipódromos de Chile: <strong>Hipódromo Chile</strong> (Santiago, Independencia),
                <strong> Club Hípico de Santiago</strong> (Blanco Encalada), <strong>Valparaíso Sporting Club</strong> (Viña del Mar)
                y <strong>Club Hípico de Concepción</strong> (Hualpén). Nuestro sistema procesa automáticamente los programas de
                carreras de cada hipódromo cuando hay jornadas programadas.
              </p>
            </div>
          </div>

          <div itemScope itemProp="mainEntity" itemType="https://schema.org/Question" style={{ marginBottom: '1.5rem', padding: '1.25rem', background: 'rgba(255,255,255,0.03)', borderRadius: '12px', borderLeft: '3px solid var(--accent)' }}>
            <h3 itemProp="name" style={{ color: 'var(--text-main)', fontSize: '1.05rem', marginBottom: '0.5rem', fontWeight: 700 }}>
              ¿Cómo puedo verificar la precisión de las predicciones?
            </h3>
            <div itemScope itemProp="acceptedAnswer" itemType="https://schema.org/Answer">
              <p itemProp="text" style={{ color: 'var(--text-muted)', margin: 0, lineHeight: 1.7, fontSize: '0.95rem' }}>
                La transparencia es uno de nuestros pilares fundamentales. Cada predicción se registra <strong>antes</strong> de la carrera
                y posteriormente se compara con los resultados oficiales. Puedes consultar nuestro rendimiento real en la{' '}
                <Link href="/precision" style={{ color: 'var(--primary)', textDecoration: 'underline' }}>sección de Precisión</Link>, donde
                mostramos las tasas de acierto para ganador exacto, quiniela, trifecta y superfecta, desglosadas por hipódromo.
              </p>
            </div>
          </div>

          <div itemScope itemProp="mainEntity" itemType="https://schema.org/Question" style={{ marginBottom: '1.5rem', padding: '1.25rem', background: 'rgba(255,255,255,0.03)', borderRadius: '12px', borderLeft: '3px solid #FFD700' }}>
            <h3 itemProp="name" style={{ color: 'var(--text-main)', fontSize: '1.05rem', marginBottom: '0.5rem', fontWeight: 700 }}>
              ¿Pista Inteligente garantiza ganancias en apuestas?
            </h3>
            <div itemScope itemProp="acceptedAnswer" itemType="https://schema.org/Answer">
              <p itemProp="text" style={{ color: 'var(--text-muted)', margin: 0, lineHeight: 1.7, fontSize: '0.95rem' }}>
                <strong>No.</strong> Pista Inteligente es una herramienta de análisis estadístico con fines informativos y de entretenimiento.
                Las carreras de caballos son eventos deportivos con un componente de incertidumbre inherente. Nuestras predicciones
                buscan identificar los caballos con mayor probabilidad estadística, pero no garantizan resultados. Siempre recomendamos
                apostar de forma responsable y dentro de sus posibilidades.
              </p>
            </div>
          </div>

          <div itemScope itemProp="mainEntity" itemType="https://schema.org/Question" style={{ padding: '1.25rem', background: 'rgba(255,255,255,0.03)', borderRadius: '12px', borderLeft: '3px solid var(--primary)' }}>
            <h3 itemProp="name" style={{ color: 'var(--text-main)', fontSize: '1.05rem', marginBottom: '0.5rem', fontWeight: 700 }}>
              ¿Cuándo se actualizan las predicciones?
            </h3>
            <div itemScope itemProp="acceptedAnswer" itemType="https://schema.org/Answer">
              <p itemProp="text" style={{ color: 'var(--text-muted)', margin: 0, lineHeight: 1.7, fontSize: '0.95rem' }}>
                Las predicciones se generan y publican automáticamente cada vez que un hipódromo publica su programa de carreras,
                generalmente la tarde anterior a cada jornada hípica. Nuestro sistema de sincronización revisa varias veces al día
                si hay nuevos programas disponibles. Una vez publicadas, las predicciones permanecen disponibles en la{' '}
                <Link href="/programa" style={{ color: 'var(--primary)', textDecoration: 'underline' }}>sección de Predicciones</Link>
                {' '}hasta que se disputan las carreras.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Hipódromos Overview */}
      <div className="glass-card" style={{ marginTop: '1.5rem' }}>
        <div className="section-title">🏟️ Hipódromos que Analizamos</div>
        <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem', lineHeight: 1.7, fontSize: '0.95rem' }}>
          Chile cuenta con una rica tradición hípica que se remonta al siglo XIX. Nuestro sistema monitorea y analiza
          las carreras de los principales recintos del país, cada uno con sus propias características y particularidades.
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
          <div style={{ padding: '1.25rem', background: 'rgba(99, 102, 241, 0.08)', borderRadius: '12px', borderLeft: '3px solid var(--primary)' }}>
            <h3 style={{ color: 'var(--primary)', marginBottom: '0.5rem', fontSize: '1.1rem' }}>🏇 Hipódromo Chile</h3>
            <p style={{ color: 'var(--text-muted)', margin: 0, fontSize: '0.9rem', lineHeight: 1.6 }}>
              Ubicado en la comuna de Independencia, Santiago. Es el hipódromo con mayor actividad del país,
              con jornadas regulares de lunes a viernes. Pista de arena de 1.500 metros.
            </p>
          </div>
          <div style={{ padding: '1.25rem', background: 'rgba(52, 211, 153, 0.08)', borderRadius: '12px', borderLeft: '3px solid var(--secondary)' }}>
            <h3 style={{ color: 'var(--secondary)', marginBottom: '0.5rem', fontSize: '1.1rem' }}>🏛️ Club Hípico de Santiago</h3>
            <p style={{ color: 'var(--text-muted)', margin: 0, fontSize: '0.9rem', lineHeight: 1.6 }}>
              Fundado en 1869, es el recinto hípico más antiguo de Chile. Ubicado en Blanco Encalada,
              Santiago. Pista de pasto de 2.000 metros. Sede de los clásicos más prestigiosos del país.
            </p>
          </div>
          <div style={{ padding: '1.25rem', background: 'rgba(16, 185, 129, 0.08)', borderRadius: '12px', borderLeft: '3px solid #10b981' }}>
            <h3 style={{ color: '#10b981', marginBottom: '0.5rem', fontSize: '1.1rem' }}>🌊 Valparaíso Sporting</h3>
            <p style={{ color: 'var(--text-muted)', margin: 0, fontSize: '0.9rem', lineHeight: 1.6 }}>
              Situado en Viña del Mar, es conocido como la cuna de la hípica chilena. Casa del Derby,
              una de las carreras clásicas más importantes de Sudamérica. Pista de pasto.
            </p>
          </div>
          <div style={{ padding: '1.25rem', background: 'rgba(245, 158, 11, 0.08)', borderRadius: '12px', borderLeft: '3px solid #f59e0b' }}>
            <h3 style={{ color: '#f59e0b', marginBottom: '0.5rem', fontSize: '1.1rem' }}>🌲 Club Hípico de Concepción</h3>
            <p style={{ color: 'var(--text-muted)', margin: 0, fontSize: '0.9rem', lineHeight: 1.6 }}>
              Ubicado en Hualpén, Región del Biobío. Principal recinto hípico del sur de Chile.
              Ofrece jornadas regulares y carreras especiales para la zona sur del país.
            </p>
          </div>
        </div>
      </div>

      <JackpotAlert />
    </>
  )
}
