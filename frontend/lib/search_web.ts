import * as cheerio from 'cheerio'

const SERPER_API_KEY = process.env.SERPER_API_KEY
const EXTERNAL_LINKS = `
- Teletrak: https://www.teletrak.cl/
- Club Hípico de Santiago: https://www.clubhipico.cl/
- Hipódromo Chile: https://www.hipodromo.cl/
- Valparaíso Sporting: https://www.sporting.cl/
`

export async function searchWeb(query: string): Promise<string> {
    try {
        // 1. Serper API (Preferred)
        if (SERPER_API_KEY) {
            const response = await fetch('https://google.serper.dev/search', {
                method: 'POST',
                headers: {
                    'X-API-KEY': SERPER_API_KEY,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ q: query, gl: 'cl', hl: 'es' })
            })

            if (response.ok) {
                const data = await response.json()
                let context = "Resultados de búsqueda web:\n"

                // Process organic results
                if (data.organic) {
                    data.organic.slice(0, 4).forEach((result: any) => {
                        context += `- [${result.title}](${result.link}): ${result.snippet}\n`
                    })
                }

                // Process knowledge graph if likely race info
                if (data.knowledgeGraph) {
                    context += `\nDatos relevantes: ${data.knowledgeGraph.description}\n`
                }

                return context
            }
        }

        // 2. Fallback: Scraping Teletrak specific pages based on keywords
        if (query.toLowerCase().includes('teletrak') || query.toLowerCase().includes('carrera')) {
            return await scrapeTeletrak()
        }

        return `No se encontró información específica. Puedes revisar manualente en:\n${EXTERNAL_LINKS}`

    } catch (e) {
        console.error('Web search failed:', e)
        return ''
    }
}

async function scrapeTeletrak(): Promise<string> {
    try {
        const response = await fetch('https://www.teletrak.cl/hipismo/carreras', {
            headers: { 'User-Agent': 'Mozilla/5.0 (compatible; PistaInteligente/1.0)' }
        })

        if (!response.ok) return ''

        const html = await response.text()
        const $ = cheerio.load(html)
        let info = '📡 Información en vivo desde Teletrak.cl:\n'

        // Example scraping logic (adjust selectors to actual site structure)
        // Teletrak often renders with JS, so this might be limited to meta tags or basic structure
        $('meta[name="description"]').each((_, el) => {
            info += `Resumen: ${$(el).attr('content')}\n`
        })

        // Basic keyword detection in body if structured data fails
        const text = $('body').text()
        if (text.includes('Valparaíso Sporting')) info += "- Valparaíso Sporting: Activo\n"
        if (text.includes('Club Hípico')) info += "- Club Hípico: Activo\n"
        if (text.includes('Hipódromo Chile')) info += "- Hipódromo Chile: Activo\n"

        return info
    } catch (e) {
        return ''
    }
}
