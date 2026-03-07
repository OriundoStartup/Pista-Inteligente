import { createClient } from '../utils/supabase/server'

export interface JineteStat {
    jinete: string
    ganadas: number
    eficiencia: string
}

/**
 * Fetches top jockeys for a specific year.
 * Uses RPC get_top_jinetes_2026 if available, otherwise falls back to manual aggregation.
 */
export async function getTopJinetes(year: number = 2026): Promise<JineteStat[]> {
    const supabase = await createClient()

    try {
        // 1. Try RPC Call (Server-side aggregation)
        const { data, error } = await supabase.rpc(`get_top_jinetes_${year}`)

        if (!error && data && data.length > 0) {
            return data.map((j: any) => ({
                jinete: j.jinete,
                ganadas: Number(j.ganadas),
                eficiencia: j.eficiencia
            }))
        }

        if (error) {
            console.warn(`RPC get_top_jinetes_${year} failed:`, error.message)
        }

        // 2. Legacy Fallback (Manual aggregation) - Subject to 1000 row limit
        const startDate = `${year}-01-01`
        const endDate = `${year}-12-31`

        const { data: legacyData, error: legacyError } = await supabase
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
            .gte('carreras.jornadas.fecha', startDate)
            .lte('carreras.jornadas.fecha', endDate)

        if (legacyError || !legacyData || legacyData.length === 0) {
            return []
        }

        // Aggregate wins and mounts
        const stats: Record<string, { ganadas: number; montes: number }> = {}

        legacyData.forEach((row: any) => {
            const jineteName = row.jinetes?.nombre || 'Desconocido'
            const nombre = jineteName.trim()

            if (!stats[nombre]) {
                stats[nombre] = { ganadas: 0, montes: 0 }
            }

            stats[nombre].montes += 1
            if (row.posicion == 1 || row.posicion == '1') {
                stats[nombre].ganadas += 1
            }
        })

        return Object.entries(stats)
            .map(([nombre, stat]) => ({
                jinete: nombre,
                ganadas: stat.ganadas,
                eficiencia: stat.montes > 0 ? ((stat.ganadas / stat.montes) * 100).toFixed(1) : '0.0'
            }))
            .sort((a, b) => b.ganadas - a.ganadas)
            .slice(0, 10)

    } catch (e) {
        console.error("Exception in getTopJinetes utility:", e)
        return []
    }
}
