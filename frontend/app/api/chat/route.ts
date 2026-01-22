import { NextResponse } from 'next/server'
import { createClient } from '../../../utils/supabase/server'

// Migrado de Gemini a Groq (2026-01-22) para mayor estabilidad
const GROQ_API_KEY = process.env.GROQ_API_KEY || ''
const GROQ_API_URL = 'https://api.groq.com/openai/v1/chat/completions'
const GROQ_MODEL = 'llama-3.3-70b-versatile' // Modelo más reciente y estable

// URLs oficiales para referencia
const EXTERNAL_LINKS = `
- Teletrak: https://www.teletrak.cl/
- Club Hípico de Santiago: https://www.clubhipico.cl/
- Hipódromo Chile: https://www.hipodromo.cl/
- Valparaíso Sporting: https://www.sporting.cl/
`

// Función para obtener información de Teletrak cuando no hay datos en Supabase
async function fetchTeletrakInfo(): Promise<string> {
    try {
        // Intentar obtener la página de carreras de Teletrak
        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), 5000) // 5s timeout

        const response = await fetch('https://www.teletrak.cl/hipismo/carreras', {
            signal: controller.signal,
            headers: {
                'User-Agent': 'Mozilla/5.0 (compatible; PistaInteligente/1.0)'
            }
        })
        clearTimeout(timeoutId)

        if (!response.ok) {
            console.log('Teletrak fetch failed:', response.status)
            return ''
        }

        const html = await response.text()

        // Extraer información básica del HTML usando regex simple
        // Buscar patrones de carreras, hipódromos y horarios
        let info = '📡 Información en vivo desde Teletrak.cl:\n'

        // Buscar menciones de hipódromos
        const hipodromos = ['Club Hípico', 'Hipódromo Chile', 'Valparaíso Sporting']
        hipodromos.forEach(h => {
            if (html.includes(h)) {
                info += `✅ ${h} tiene carreras programadas hoy\n`
            }
        })

        // Buscar horarios (patrón HH:MM)
        const horasMatch = html.match(/\b([0-1]?[0-9]|2[0-3]):[0-5][0-9]\b/g)
        if (horasMatch && horasMatch.length > 0) {
            const horasUnicas = [...new Set(horasMatch)].slice(0, 5)
            info += `⏰ Horarios encontrados: ${horasUnicas.join(', ')}\n`
        }

        info += '\n👉 Para ver el programa completo visita: https://www.teletrak.cl/hipismo/carreras'

        return info
    } catch (e) {
        console.log('Teletrak scraping failed (timeout or error):', e)
        return ''
    }
}

async function getUpcomingRaces(): Promise<string> {
    try {
        const supabase = await createClient()
        const today = new Date().toISOString().split('T')[0]

        if (!GROQ_API_KEY) {
            console.error('❌ GROQ_API_KEY is missing in environment variables')
            // Don't return here, let it fail in getGroqResponse to trigger fallback, 
            // but logging is crucial for debugging.
        }

        // Consultar próximas 3 carreras de hoy o futuro inmediato
        const { data: carreras, error } = await supabase
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
                    jinete:jinetes (nombre),
                    prediccion:predicciones (rank_predicho, probabilidad)
                )
            `)
            .gte('jornada.fecha', today)
            .order('jornada(fecha)', { ascending: true })
            .order('hora', { ascending: true })
            .limit(3)

        if (error) {
            console.error('Error fetching races for chatbot:', error)
            return ''
        }

        if (!carreras || carreras.length === 0) {
            // Fallback: intentar obtener info de Teletrak
            console.log('No races in Supabase, fetching from Teletrak...')
            const teletrakInfo = await fetchTeletrakInfo()
            if (teletrakInfo) {
                return teletrakInfo
            }
            return 'No hay carreras programadas próximamente. Visita https://www.teletrak.cl para ver el programa actualizado.'
        }

        let context = "Información en tiempo real de las próximas carreras:\n"

        carreras.forEach((c: any) => {
            // @ts-ignore
            const hipodromo = c.jornada?.hipodromo?.nombre || 'Hipódromo'
            // @ts-ignore
            const fecha = c.jornada?.fecha || today

            context += `\n🏁 ${hipodromo} - ${fecha} - Carrera ${c.numero} (${c.hora || 'Hora TBD'}, ${c.distancia || '?'}m):\n`

            // Filtrar top predicciones si existen
            // @ts-ignore
            if (c.participaciones && c.participaciones.length > 0) {
                // Participaciones no siempre tiene predicciones linkeadas directamente en esta query compleja,
                // simplificamos mostrando caballos confirmados
                const favoritos = c.participaciones
                    .slice(0, 4)
                    // @ts-ignore
                    .map(p => `- ${p.caballo?.nombre} (Jinete: ${p.jinete?.nombre || 'N/A'})`)
                    .join('\n')
                context += `Principales inscritos:\n${favoritos}\n`
            }
        })

        return context
    } catch (e) {
        console.error('Error constructing race context:', e)
        return ''
    }
}

async function getGroqResponse(userMessage: string, raceContext: string): Promise<string> {
    const SYSTEM_PROMPT = `Actúa como "Pista Inteligente Analyst", un experto en hípica chilena.
    
CONTEXTO ACTUAL (DATOS REALES):
${raceContext}

RECURSOS EXTERNOS (Úsalos si el usuario pide ver carreras o apostar):
${EXTERNAL_LINKS}

TU CONOCIMIENTO:
- Usas un modelo de IA Ensemble (LightGBM + XGBoost + CatBoost) con ~24% precisión a ganador.
- Analizas factores como velocidad, jinete, peso y distancia.

REGLAS DE RESPUESTA:
1. Sé analítico pero accesible. Usa emojis hípicos (🏇, 🏆, ⏱️).
2. Si preguntan por una carrera específica, USA LOS DATOS DEL CONTEXTO.
3. Si el usuario pide enlaces, dale los de Teletrak o el hipódromo correspondiente.
4. Si no hay datos de la carrera que piden, di que "aún no está en mi sistema" y sugiere mirar Teletrak.
5. Responde SIEMPRE en español conciso, máximo 3-4 oraciones.`

    try {
        const response = await fetch(GROQ_API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${GROQ_API_KEY}`
            },
            body: JSON.stringify({
                model: GROQ_MODEL,
                messages: [
                    { role: 'system', content: SYSTEM_PROMPT },
                    { role: 'user', content: userMessage }
                ],
                temperature: 0.5,
                max_tokens: 350
            })
        })

        if (!response.ok) {
            const err = await response.text()
            throw new Error(`Groq API error ${response.status}: ${err}`)
        }

        const data = await response.json()
        const text = data.choices?.[0]?.message?.content

        if (!text) throw new Error('Empty response from Groq')
        return text.trim()

    } catch (error) {
        console.error('Groq Interaction Failed:', error)
        throw error
    }
}

const fallbackResponses: Record<string, string> = {
    'hola': '¡Hola! 🏇 Soy tu analista de Pista Inteligente. ¿Quieres información sobre las carreras de hoy o necesitas enlaces a Teletrak?',
    'default': 'Estoy teniendo problemas para conectar con mi cerebro de IA, pero puedes ver las predicciones en el menú principal o visitar Teletrak.cl para ver las carreras en vivo.'
}

// Simple Cache System
const responseCache = new Map<string, { response: string, timestamp: number }>();
const CACHE_DURATION = 1000 * 60 * 10; // 10 minutes cache logic

function getFallbackResponse(message: string): string {
    const msgLower = message.toLowerCase()
    if (msgLower.includes('hola') || msgLower.includes('buenos')) return fallbackResponses['hola']
    return fallbackResponses['default']
}

export async function POST(request: Request) {
    try {
        const { message } = await request.json()

        if (!message || typeof message !== 'string') {
            return NextResponse.json({ response: 'Mensaje inválido' }, { status: 400 })
        }

        // Cache Check
        const cacheKey = message.trim().toLowerCase();
        const cached = responseCache.get(cacheKey);
        if (cached && (Date.now() - cached.timestamp < CACHE_DURATION)) {
            // Return cached response if valid
            return NextResponse.json({ response: cached.response });
        }

        try {
            // 1. Obtener contexto en tiempo real
            // (Optimize: Context fetching could also be cached, but race data changes. 
            // For now, let's cache only the AI response for specific questions)
            const raceContext = await getUpcomingRaces()

            // 2. Consultar a Groq (Llama 3.3 70B)
            const aiResponse = await getGroqResponse(message, raceContext)

            // Save to Cache
            responseCache.set(cacheKey, { response: aiResponse, timestamp: Date.now() });

            // Limit cache size to prevent memory leaks in serverless
            if (responseCache.size > 100) {
                const firstKey = responseCache.keys().next().value;
                if (firstKey) responseCache.delete(firstKey);
            }

            return NextResponse.json({ response: aiResponse })
        } catch (error) {
            console.error('Chat API Error:', error)
            const fallback = getFallbackResponse(message)
            return NextResponse.json({ response: fallback })
        }

    } catch (e) {
        return NextResponse.json({ response: 'Error interno del servidor' }, { status: 500 })
    }
}
