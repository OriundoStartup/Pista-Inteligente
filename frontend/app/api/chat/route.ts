import { NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'

const GEMINI_API_KEY = process.env.GEMINI_API_KEY || ''
const GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent'

// URLs oficiales para referencia
const EXTERNAL_LINKS = `
- Teletrak: https://www.teletrak.cl/
- Club Hípico de Santiago: https://www.clubhipico.cl/
- Hipódromo Chile: https://www.hipodromo.cl/
- Valparaíso Sporting: https://www.sporting.cl/
`

async function getUpcomingRaces(): Promise<string> {
    try {
        const today = new Date().toISOString().split('T')[0]

        if (!GEMINI_API_KEY) {
            console.error('❌ GEMINI_API_KEY is missing in environment variables')
            // Don't return here, let it fail in getGeminiResponse to trigger fallback, 
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
            return 'No hay carreras programadas próximamente en la base de datos.'
        }

        let context = "Información en tiempo real de las próximas carreras:\n"

        carreras.forEach(c => {
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

async function getGeminiResponse(userMessage: string, raceContext: string): Promise<string> {
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
5. Responde SIEMPRE en español conciso.

Usuario: ${userMessage}
Asistente:`

    try {
        const response = await fetch(`${GEMINI_API_URL}?key=${GEMINI_API_KEY}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                contents: [{
                    parts: [{ text: SYSTEM_PROMPT }]
                }],
                generationConfig: {
                    temperature: 0.5, // Más preciso
                    maxOutputTokens: 350,
                }
            })
        })

        if (!response.ok) {
            const err = await response.text()
            throw new Error(`Gemini API error ${response.status}: ${err}`)
        }

        const data = await response.json()
        const text = data.candidates?.[0]?.content?.parts?.[0]?.text

        if (!text) throw new Error('Empty response from Gemini')
        return text.trim()

    } catch (error) {
        console.error('Gemini Interaction Failed:', error)
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

            // 2. Consultar a Gemini
            const aiResponse = await getGeminiResponse(message, raceContext)

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
