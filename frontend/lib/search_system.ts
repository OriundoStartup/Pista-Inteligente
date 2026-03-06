import { createClient } from '../utils/supabase/server'

const INTENT_KEYWORDS: Record<string, string[]> = {
    carreras_hoy: ['carrera', 'hoy', 'hipico', 'programa', 'programacion', 'tarde', 'mañana', 'esta noche', 'corren'],
    partantes: ['partante', 'anotado', 'inscrito', 'participan', 'corredores', 'caballos'],
    resultados: ['resultado', 'ganó', 'gano', 'ganador', 'primero', 'llegó', 'llego', 'pagó', 'pago'],
    estadisticas: ['estadística', 'estadistica', 'historial', 'récord', 'record', 'rendimiento', 'promedio'],
    quiniela: ['quiniela', 'apuesta', 'combinación', 'combinacion', 'trifecta', 'superfecta', 'exacta'],
};

function detectIntent(query: string): string[] {
    const normalizedQuery = query
        .toLowerCase()
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "");

    const detectedIntents: string[] = [];

    for (const [intent, keywords] of Object.entries(INTENT_KEYWORDS)) {
        if (keywords.some(keyword => normalizedQuery.includes(keyword))) {
            detectedIntents.push(intent);
        }
    }

    return detectedIntents.length > 0 ? detectedIntents : ['general'];
}

export async function searchSystem(query: string): Promise<string> {
    const supabase = await createClient()
    const today = new Date().toISOString().split('T')[0]
    let results = ''

    const intents = detectIntent(query);
    console.log('[search_system] Intenciones detectadas:', intents);

    try {
        // 1. Búsqueda de Carreras / Programación
        if (intents.includes('carreras_hoy') || intents.includes('partantes')) {
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
                .limit(20)

            if (carreras && carreras.length > 0) {
                results += `🏁 **Programación encontrada (${carreras.length} carreras):**\n`
                carreras.forEach((c: any) => {
                    const hipodromo = c.jornada?.hipodromo?.nombre
                    const fecha = c.jornada?.fecha
                    results += `- ${hipodromo} (${fecha}) Carrera ${c.numero} a las ${c.hora}. Distancia: ${c.distancia}m.\n`
                })
                results += "\n"
            }
        }

        // 2. Búsqueda de Jinetes / Estadísticas
        if (intents.includes('estadisticas') || intents.includes('general')) {
            const { data: jinetes } = await supabase
                .from('jinetes')
                .select('nombre, estadisticas_jinetes(triunfos, eficiencia)')
                .ilike('nombre', `%${query}%`)
                .limit(10)

            if (jinetes && jinetes.length > 0) {
                results += `🏇 **Jinetes Encontrados (${jinetes.length}):**\n`
                jinetes.forEach(j => {
                    const stats = j.estadisticas_jinetes?.[0]
                    results += `- ${j.nombre}: ${stats ? `${stats.triunfos} triunfos, ${stats.eficiencia}% eficiencia` : 'Sin estadísticas recientes'}\n`
                })
                results += "\n"
            }
        }

        return results
    } catch (e) {
        console.error('Error in searchSystem:', e)
        return ''
    }
}
