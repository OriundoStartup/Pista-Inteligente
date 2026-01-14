import { supabase } from '@/lib/supabase'
import { Trophy, TrendingUp, Users, MapPin, ArrowRight, Zap } from 'lucide-react'
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

const getStats = async (): Promise<Stats> => {
  // In a real scenario, this would call a Supabase RPC or view?
  // For now we mock or query basic counts if possible.
  // Since we haven't migrated data yet, we return valid placeholders 
  // or try to query if env is set.

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

  return (
    <div className="min-h-screen bg-neutral-900 text-white font-sans selection:bg-emerald-500 selection:text-white">
      {/* Navbar */}
      <nav className="border-b border-white/10 backdrop-blur-md sticky top-0 z-50 bg-neutral-900/80">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Zap className="text-emerald-400 w-6 h-6" />
            <span className="font-bold text-xl tracking-tight">Pista Inteligente</span>
          </div>
          <div className="hidden md:flex gap-8 text-sm font-medium text-neutral-400">
            <Link href="/programa" className="hover:text-white transition-colors">Programa</Link>
            <Link href="/analisis" className="hover:text-white transition-colors">Análisis IA</Link>
            <Link href="/precision" className="hover:text-white transition-colors">Precisión</Link>
            <Link href="/blog" className="hover:text-white transition-colors">Blog</Link>
          </div>
          <Link href="/login" className="bg-emerald-500 hover:bg-emerald-600 text-white px-4 py-2 rounded-full text-sm font-medium transition-transform active:scale-95">
            Ingresar
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <header className="relative py-24 px-6 overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,_var(--tw-gradient-stops))] from-emerald-900/20 via-neutral-900 to-neutral-900 -z-10" />
        <div className="max-w-7xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-semibold mb-6 border border-emerald-500/20">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            IA Hípica v4.0 Activa
          </div>
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-8 bg-gradient-to-br from-white to-neutral-500 bg-clip-text text-transparent">
            Predice el Futuro de la Hípica
          </h1>
          <p className="text-xl text-neutral-400 max-w-2xl mx-auto mb-10 leading-relaxed">
            Utilizamos Inteligencia Artificial avanzada para analizar miles de carreras y detectar patrones ganadores en Chile.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/programa" className="group flex items-center justify-center gap-2 bg-white text-neutral-900 px-8 py-4 rounded-full font-bold text-lg hover:bg-neutral-200 transition-all">
              Ver Predicciones Hoy
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link href="/precision" className="flex items-center justify-center gap-2 px-8 py-4 rounded-full font-bold text-lg border border-white/20 hover:bg-white/10 transition-all backdrop-blur-sm">
              Ver Transparencia
            </Link>
          </div>
        </div>
      </header>

      {/* Stats Grid */}
      <section className="py-20 px-6 border-t border-white/5">
        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="p-8 rounded-3xl bg-neutral-800/50 border border-white/5 hover:border-emerald-500/30 transition-colors group">
            <div className="w-12 h-12 rounded-2xl bg-emerald-500/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <Trophy className="w-6 h-6 text-emerald-400" />
            </div>
            <h3 className="text-4xl font-bold mb-2">{stats.aciertos_ultimo_mes}%</h3>
            <p className="text-neutral-400 font-medium">Precisión Top 1 (Ult. Mes)</p>
          </div>
          <div className="p-8 rounded-3xl bg-neutral-800/50 border border-white/5 hover:border-purple-500/30 transition-colors group">
            <div className="w-12 h-12 rounded-2xl bg-purple-500/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <TrendingUp className="w-6 h-6 text-purple-400" />
            </div>
            <h3 className="text-4xl font-bold mb-2">${(stats.dividendos_generados / 1000).toFixed(0)}k</h3>
            <p className="text-neutral-400 font-medium">Dividendos Generados</p>
          </div>
          <div className="p-8 rounded-3xl bg-neutral-800/50 border border-white/5 hover:border-blue-500/30 transition-colors group">
            <div className="w-12 h-12 rounded-2xl bg-blue-500/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <Users className="w-6 h-6 text-blue-400" />
            </div>
            <h3 className="text-4xl font-bold mb-2">{stats.total_carreras}</h3>
            <p className="text-neutral-400 font-medium">Carreras Analizadas</p>
          </div>
        </div>
      </section>

      {/* Top Jinetes Preview */}
      <section className="py-20 px-6 bg-neutral-800/30">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-12">
            <h2 className="text-3xl font-bold">Jinetes en Racha 🔥</h2>
            <Link href="/estadisticas" className="text-emerald-400 hover:text-emerald-300 font-medium">Ver todos</Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {stats.jinetes.map((j, i) => (
              <div key={i} className="flex items-center gap-4 p-4 rounded-xl bg-neutral-900 border border-white/5">
                <div className="w-10 h-10 rounded-full bg-neutral-800 flex items-center justify-center font-bold text-neutral-500">
                  {i + 1}
                </div>
                <div>
                  <h4 className="font-bold">{j.jinete}</h4>
                  <p className="text-sm text-emerald-400">{j.eficiencia}% Eficiencia</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-white/10 text-center text-neutral-500 text-sm">
        <p>&copy; 2026 Pista Inteligente. Powered by Supabase & Vercel.</p>
      </footer>
    </div>
  )
}
