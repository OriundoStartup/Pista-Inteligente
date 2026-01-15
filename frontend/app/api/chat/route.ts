import { NextResponse } from 'next/server'

const GEMINI_API_KEY = process.env.GEMINI_API_KEY || ''
const GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent'

const SYSTEM_CONTEXT = `Eres el asistente de IA de "Pista Inteligente", una plataforma de predicciones hípicas con inteligencia artificial para el Hipódromo Chile y Club Hípico de Chile.

Tu conocimiento incluye:
- Predicciones de carreras usando un modelo ensemble (LightGBM, XGBoost, CatBoost)
- Precisión del modelo: ~24% Top-1, ~58% Top-3, ~72% Top-4
- Factores como jinete, caballo, distancia, peso, descanso entre carreras
- Hipódromos cubiertos: Hipódromo Chile y Club Hípico de Santiago

Reglas:
- Responde SIEMPRE en español
- Sé amigable y conciso (máximo 2-3 oraciones)
- Si preguntan por predicciones específicas, dirige a la sección "Predicciones" del sitio
- Nunca inventes datos de carreras o caballos específicos
- Si no sabes algo, admítelo honestamente`

async function getGeminiResponse(userMessage: string): Promise<string> {
    try {
        const response = await fetch(`${GEMINI_API_URL}?key=${GEMINI_API_KEY}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                contents: [{
                    parts: [{
                        text: `${SYSTEM_CONTEXT}\n\nUsuario: ${userMessage}\n\nAsistente:`
                    }]
                }],
                generationConfig: {
                    temperature: 0.7,
                    maxOutputTokens: 256,
                    topP: 0.8,
                    topK: 40
                }
            })
        })

        if (!response.ok) {
            throw new Error(`Gemini API error: ${response.status}`)
        }

        const data = await response.json()
        const text = data.candidates?.[0]?.content?.parts?.[0]?.text

        if (!text) {
            throw new Error('No response from Gemini')
        }

        return text.trim()
    } catch (error) {
        console.error('Gemini API error:', error)
        throw error
    }
}

// Respuestas de fallback si Gemini falla
const fallbackResponses: Record<string, string> = {
    'hola': '¡Hola! Soy el asistente de Pista Inteligente. ¿En qué puedo ayudarte?',
    'predicciones': 'Las predicciones están en la sección "Predicciones" del menú. Usamos IA con LightGBM, XGBoost y CatBoost.',
    'precision': 'Nuestra precisión Top-1 es ~24% y Top-4 supera el 70%. Puedes ver más en la página de Precisión.',
    'default': 'Puedo ayudarte con información sobre predicciones, precisión del modelo, o estadísticas. ¿Qué te gustaría saber?'
}

function getFallbackResponse(message: string): string {
    const msgLower = message.toLowerCase()
    for (const [key, response] of Object.entries(fallbackResponses)) {
        if (msgLower.includes(key)) return response
    }
    return fallbackResponses.default
}

export async function POST(request: Request) {
    try {
        const { message } = await request.json()

        if (!message || typeof message !== 'string') {
            return NextResponse.json(
                { response: 'Por favor, escribe un mensaje válido.' },
                { status: 400 }
            )
        }

        try {
            // Intentar con Gemini AI
            const geminiResponse = await getGeminiResponse(message)
            return NextResponse.json({ response: geminiResponse })
        } catch {
            // Fallback a respuestas predefinidas
            const fallback = getFallbackResponse(message)
            return NextResponse.json({ response: fallback })
        }

    } catch {
        return NextResponse.json(
            { response: 'Lo siento, hubo un error. Por favor intenta de nuevo.' },
            { status: 500 }
        )
    }
}
