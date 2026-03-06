import { NextResponse } from 'next/server'
import { withCors, corsOptionsResponse } from '../../../lib/cors'
import { searchSystem } from '../../../lib/search_system'
import { searchWeb } from '../../../lib/search_web'

// Handle CORS preflight
export const OPTIONS = corsOptionsResponse;

// --- PROVIDER CONFIGURATION ---

// 1. Gemini (Google AI) - Prioridad Local
const GEMINI_API_KEY = process.env.GEMINI_API_KEY || ''
const GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent'

// 2. Groq (Llama 3.3) - Prioridad Vercel / Producción
const GROQ_API_KEY = process.env.GROQ_API_KEY || ''
const GROQ_API_URL = 'https://api.groq.com/openai/v1/chat/completions'
const GROQ_MODEL = 'llama-3.3-70b-versatile'

async function getGeminiResponse(userMessage: string, systemPrompt: string, history: any[] = []): Promise<string> {
    // Mapear historial al formato de Gemini (user/model)
    const contents = [
        ...history.map(h => ({
            role: h.role === 'assistant' ? 'model' : 'user',
            parts: [{ text: h.content }]
        })),
        {
            role: 'user',
            parts: [{ text: `${systemPrompt}\n\nPREGUNTA USUARIO:\n${userMessage}` }]
        }
    ]

    const response = await fetch(`${GEMINI_API_URL}?key=${GEMINI_API_KEY}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            contents,
            generationConfig: { maxOutputTokens: 400 }
        })
    })

    if (!response.ok) throw new Error(`Gemini API error ${response.status}`)
    const data = await response.json()
    return data.candidates?.[0]?.content?.parts?.[0]?.text?.trim() || 'Sin respuesta de Gemini'
}

async function getGroqResponse(userMessage: string, systemPrompt: string, history: any[] = []): Promise<string> {
    const messages = [
        { role: 'system', content: systemPrompt },
        ...history,
        { role: 'user', content: userMessage }
    ]

    const response = await fetch(GROQ_API_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${GROQ_API_KEY}`
        },
        body: JSON.stringify({
            model: GROQ_MODEL,
            messages,
            temperature: 0.5,
            max_tokens: 400
        })
    })

    if (!response.ok) throw new Error(`Groq API error ${response.status}`)
    const data = await response.json()
    return data.choices?.[0]?.message?.content?.trim() || 'Sin respuesta de Groq'
}

async function getAIResponse(userMessage: string, context: string, history: any[] = []): Promise<string> {
    const SYSTEM_PROMPT = `Actúa como "Pista Inteligente Analyst", un experto en hípica chilena.
    
CONTEXTO RECUPERADO (SISTEMA + WEB):
${context}

TU CONOCIMIENTO:
- Eres experto en datos de carreras, jinetes y caballos.
- Usas un modelo de IA Ensemble para predicciones.

REGLAS DE RESPUESTA:
1. Sé analítico pero accesible. Usa emojis hípicos (🏇, 🏆, ⏱️).
2. BASA TU RESPUESTA EN EL CONTEXTO PROPORCIONADO. Si el contexto tiene la respuesta, úsala.
3. Si el contexto indica "Búsqueda web", cita la fuente. Si los datos son escasos, sugiere al usuario revisar el programa oficial en Teletrak.cl o ClubHipico.cl.
4. Si no tienes información suficiente, no inventes datos. Indica qué encontraste y qué falta.
5. Responde SIEMPRE en español, máximo 5 oraciones.`

    // Lógica de Selección de Proveedor
    if (GEMINI_API_KEY) {
        try {
            console.log("Usando proveedor: Gemini")
            return await getGeminiResponse(userMessage, SYSTEM_PROMPT, history)
        } catch (e) {
            console.error("Gemini falló, intentando fallback...", e)
        }
    }

    if (GROQ_API_KEY) {
        try {
            console.log("Usando proveedor: Groq")
            return await getGroqResponse(userMessage, SYSTEM_PROMPT, history)
        } catch (e) {
            console.error("Groq falló", e)
        }
    }

    return "Lo siento, no puedo conectar con mi cerebro de IA en este momento (Faltan API Keys válidas)."
}

const fallbackResponses: Record<string, string> = {
    'hola': '¡Hola! 🏇 Soy tu analista de Pista Inteligente. Puedo buscar información sobre carreras, jinetes o resultados. ¿Qué necesitas?',
    'default': 'Estoy teniendo problemas para conectar con mi cerebro de IA. Por favor intenta más tarde o visita Teletrak.cl.'
}

// TODO: Implementar caché con Redis (Upstash) o Supabase para ambientes serverless
// No usar Map() en memoria: no persiste entre invocaciones en Vercel/Netlify


export async function POST(request: Request) {
    try {
        const { message, history = [] } = await request.json()

        if (!message || typeof message !== 'string' || message.trim().length === 0) {
            return withCors(NextResponse.json(
                { error: 'Mensaje requerido' },
                { status: 400 }
            ))
        }

        const trimmedMessage = message.trim();

        if (trimmedMessage.length > 500) {
            return withCors(NextResponse.json(
                { error: 'Mensaje demasiado largo. Máximo 500 caracteres.' },
                { status: 400 }
            ))
        }

        // Validar historial (máximo 10 mensajes previos)
        const safeHistory = Array.isArray(history) ? history.slice(-10) : []

        const sanitizedMessage = trimmedMessage.replace(/[<>{}]/g, '').slice(0, 500);


        try {
            // 1. Ejecutar búsquedas en paralelo (Sistema + Web)
            const [systemInfo, webResult] = await Promise.all([
                searchSystem(sanitizedMessage),
                searchWeb(sanitizedMessage)
            ])

            const webInfo = webResult.success ? webResult.data : "";

            const combinedContext = `
--- INFORMACIÓN DEL SISTEMA ---
${systemInfo || "No se encontraron datos internos relevantes."}

--- INFORMACIÓN EXTERNA (WEB) ---
${webInfo || (webResult.error ? `Error: ${webResult.error}` : "No se encontraron datos externos relevantes.")}
            `

            // 2. Consultar a la IA (Dinámica)
            const aiResponse = await getAIResponse(sanitizedMessage, combinedContext, safeHistory)

            return withCors(NextResponse.json({ response: aiResponse }))
        } catch (error) {
            console.error('Chat API Error:', error)
            const fallback = sanitizedMessage.toLowerCase().includes('hola') ? fallbackResponses['hola'] : fallbackResponses['default']
            return withCors(NextResponse.json({ response: fallback }))
        }

    } catch (e) {
        return withCors(NextResponse.json({ error: 'Error interno del servidor' }, { status: 500 }))
    }
}
