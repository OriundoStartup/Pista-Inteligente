import { supabase } from '@/lib/supabase'
import { Trophy, TrendingUp, Users, MapPin, ArrowRight } from 'lucide-react'
import Link from 'next/link'

// Types
type Stats = {
  total_carreras: number
  aciertos_ultimo_mes: number
  dividendos_generados: number
  jinetes: any[]
  caballos: any[]
  pistas: any[]
}

const getPrograms = async () => {
  const { data: jornadas, error } = await supabase
    .from('jornadas')
    .select(`
      id,
      fecha,
      reunion,
      hipodromos (
        nombre
      )
    `)
    .gte('fecha', new Date().toISOString().split('T')[0]) // From today onwards
    .order('fecha', { ascending: true })
    .limit(6)

  if (error) {
    console.error('Error fetching programs:', error)
    return []
  }
  return jornadas
}

const getStats = async (): Promise<Stats> => {
  // Mock stats for now until we have history
  return {
    total_carreras: 1250,
    aciertos_ultimo_mes: 85.4,
    dividendos_generados: 1250000,
    jinetes: [
      { jinete: 'J. Medina', eficiencia: 28.5, ganadas: 45 },
      { jinete: 'B. Sancho', eficiencia: 24.1, ganadas: 38 },
      { jinete: 'K. Espina', eficiencia: 21.0, ganadas: 30 },
    ],
    caballos: [
      { caballo: 'Shark', ganadas: 5 },
      { caballo: 'El Mero Mero', ganadas: 4 },
      { caballo: 'Doña Tota', ganadas: 4 },
    ],
    pistas: []
  }
}

export default async function Home() {
  const stats = await getStats()
  const programs = await getPrograms()

  return (
    <div className="min-h-screen text-white font-sans selection:bg-emerald-500 selection:text-white">
      {/* Navbar */}
      <nav className="glass-header">
        <div className="brand">
          <img src="/logo.png" alt="Pista Inteligente" className="h-10 w-auto" />
          <span className="hidden sm:block">Pista Inteligente</span>
        </div>
        <div className="nav-links hidden md:flex">
          <Link href="/programa" className="nav-link">Programa</Link>
          <Link href="/analisis" className="nav-link">Análisis IA</Link>
          <Link href="/precision" className="nav-link">Precisión</Link>
          <Link href="/blog" className="nav-link">Blog</Link>
        </div>
        <Link href="/login" className="cta-button text-sm px-6 py-2">
          Ingresar
        </Link>
      </nav>

      {/* Hero Section */}
      <header className="hero">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-semibold mb-6 border border-emerald-500/20">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          IA Hípica v4.0 Activa
        </div>
        <h1>
          Predice el Futuro de la Hípica
        </h1>
        <p>
          Utilizamos Inteligencia Artificial avanzada para analizar miles de carreras y detectar patrones ganadores en Chile.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link href="/programa" className="cta-button group">
            Ver Predicciones Hoy
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </Link>
        </div>
      </header>

      {/* Programas (Upcoming Races) - NEW SECTION */}
      <section className="container py-12">
        <h2 className="section-title">Próximos Programas 📅</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {programs && programs.length > 0 ? (
            programs.map((prog: any) => (
              <Link key={prog.id} href={`/programa/${prog.fecha}`} className="glass-card hover:bg-white/5 block group no-underline text-white">
                <div className="flex justify-between items-start mb-4">
                  <span className="bg-emerald-500/20 text-emerald-400 text-xs font-bold px-3 py-1 rounded-full border border-emerald-500/20">
                    {prog.reunion || 'Programa Oficial'}
                  </span>
                  <span className="text-neutral-400 text-sm">{prog.fecha}</span>
                </div>
                <h3 className="text-xl font-bold mb-2 group-hover:text-emerald-400 transition-colors">
                  {prog.hipodromos?.nombre || 'Hipódromo'}
                </h3>
                <div className="flex items-center text-sm text-neutral-400 gap-2">
                  <MapPin className="w-4 h-4" />
                  <span>Chile</span>
                </div>
              </Link>
            ))
          ) : (
            <div className="col-span-full text-center py-12 text-neutral-500 bg-white/5 rounded-2xl border border-white/5 border-dashed">
              <p>No se encontraron programas futuros disponibles. (Revisa si el worker corrió hoy)</p>
            </div>
          )}
        </div>
      </section>

      {/* Stats Grid */}
      <section className="container py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="glass-card group flex flex-col items-center text-center">
            <div className="w-16 h-16 rounded-2xl bg-emerald-500/20 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
              <Trophy className="w-8 h-8 text-emerald-400" />
            </div>
            <h3 className="text-4xl font-bold mb-2 text-emerald-400">{stats.aciertos_ultimo_mes}%</h3>
            <p className="text-neutral-400 font-medium">Precisión Top 1 (Ult. Mes)</p>
          </div>
          <div className="glass-card group flex flex-col items-center text-center">
            <div className="w-16 h-16 rounded-2xl bg-purple-500/20 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
              <TrendingUp className="w-8 h-8 text-purple-400" />
            </div>
            <h3 className="text-4xl font-bold mb-2 text-purple-400">${(stats.dividendos_generados / 1000).toFixed(0)}k</h3>
            <p className="text-neutral-400 font-medium">Dividendos Generados</p>
          </div>
          <div className="glass-card group flex flex-col items-center text-center">
            <div className="w-16 h-16 rounded-2xl bg-blue-500/20 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
              <Users className="w-8 h-8 text-blue-400" />
            </div>
            <h3 className="text-4xl font-bold mb-2 text-blue-400">{stats.total_carreras}</h3>
            <p className="text-neutral-400 font-medium">Carreras Analizadas</p>
          </div>
        </div>
      </section>

      {/* Top Jinetes Preview */}
      <section className="container py-12 relative">
        <div className="glass-card">
          <div className="flex items-center justify-between mb-8 px-4">
            <h2 className="section-title !mb-0 !border-l-0 !pl-0">Jinetes en Racha 🔥</h2>
            <Link href="/estadisticas" className="nav-link !p-0 hover:!bg-transparent text-emerald-400 hover:text-emerald-300">Ver todos</Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {stats.jinetes.map((j, i) => (
              <div key={i} className="flex items-center gap-4 p-4 rounded-xl border border-white/5 bg-black/20 hover:bg-black/40 transition-colors">
                <div className="w-10 h-10 rounded-full bg-neutral-800 flex items-center justify-center font-bold text-neutral-500 border border-white/10">
                  {i + 1}
                </div>
                <div>
                  <h4 className="font-bold text-lg">{j.jinete}</h4>
                  <p className="text-sm text-emerald-400 font-mono">{j.eficiencia}% Eficiencia</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="site-footer">
        <div className="footer-content">
          <p className="copyright">&copy; 2026 Pista Inteligente. Powered by Supabase & Vercel.</p>
        </div>
      </footer>
    </div>
  )
}
