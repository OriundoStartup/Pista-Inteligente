import { createClient } from '../utils/supabase/server'

export async function searchSystem(query: string): Promise<string> {
    const supabase = await createClient()
    const today = new Date().toISOString().split('T')[0]
    let results = ''

    try {
        // 1. Busqueda de Carreras (por hipódromo o fecha próxima)
        if (query.toLowerCase().includes('carrera') || query.toLowerCase().includes('hoy') || query.toLowerCase().includes('proxima')) {
            const { data: carreras } = await supabase
                .from('carreras')
                .select(`
                    numero,
                    hora,
                    distancia,
                    jornada:jornadas!inner (
                        fecha,
                        hipodromo:hipodromos!inner (nombre)
                    ),
                    participaciones (
                        caballo:caballos (nombre),
                        jinete:jinetes (nombre)
                    )
                `)
                .gte('jornada.fecha', today)
                .order('jornada(fecha)', { ascending: true })
                .order('hora', { ascending: true })
                .limit(3)

            if (carreras && carreras.length > 0) {
                results += "🏁 **Próximas Carreras:**\n"
                carreras.forEach((c: any) => {
                    const hipodromo = c.jornada?.hipodromo?.nombre
                    const fecha = c.jornada?.fecha
                    results += `- ${hipodromo} (${fecha}) Carrera ${c.numero} a las ${c.hora}. Distancia: ${c.distancia}m.\n`
                })
                results += "\n"
            }
        }

        // 2. Busqueda de Jinetes (si la query parece un nombre)
        // Heurística simple: si no es comando de sistema, buscamos coincidencias de texto
        if (!process.env.GROQ_API_KEY) {
            // Si no hay IA para decidir, hacemos búsqueda básica de texto
            // En implementación final, la IA decide qué buscar, pero aquí dejamos herramientas listas.
        }

        // Búsqueda genérica en Jinetes
        const { data: jinetes } = await supabase
            .from('jinetes')
            .select('nombre, estadisticas_jinetes(triunfos, eficiencia)')
            .ilike('nombre', `%${query}%`)
            .limit(3)

        if (jinetes && jinetes.length > 0) {
            results += "🏇 **Jinetes Encontrados:**\n"
            jinetes.forEach(j => {
                const stats = j.estadisticas_jinetes?.[0]
                results += `- ${j.nombre}: ${stats ? `${stats.triunfos} triunfos, ${stats.eficiencia}% eficiencia` : 'Sin estadísticas recientes'}\n`
            })
            results += "\n"
        }

        return results
    } catch (e) {
        console.error('Error in searchSystem:', e)
        return ''
    }
}
