import * as cheerio from 'cheerio'

const SERPER_API_KEY = process.env.SERPER_API_KEY
const EXTERNAL_LINKS = `
- Teletrak: https://www.teletrak.cl/
- Club Hípico de Santiago: https://www.clubhipico.cl/
- Hipódromo Chile: https://www.hipodromo.cl/
- Valparaíso Sporting: https://www.sporting.cl/
`

export type WebSearchResult = {
    success: boolean;
    data: string;
    source: string;
    error?: string
};

export async function searchWeb(query: string): Promise<WebSearchResult> {
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

                if (data.organic) {
                    data.organic.slice(0, 4).forEach((result: any) => {
                        context += `- [${result.title}](${result.link}): ${result.snippet}\n`
                    })
                }

                if (data.knowledgeGraph) {
                    context += `\nDatos relevantes: ${data.knowledgeGraph.description}\n`
                }

                return { success: true, data: context, source: 'Serper API' }
            }
        }

        // 2. Fallback: Scraping Teletrak robusto
        if (query.toLowerCase().includes('teletrak') || query.toLowerCase().includes('carrera') || query.toLowerCase().includes('partantes')) {
            return await scrapeTeletrak()
        }

        return {
            success: false,
            data: `No se encontró información específica. Puedes revisar manualmente en:\n${EXTERNAL_LINKS}`,
            source: 'Fallback Links'
        }

    } catch (e) {
        console.error('Web search overall failure:', e)
        return { success: false, data: '', source: 'None', error: 'Error general en búsqueda web' }
    }
}

async function scrapeTeletrak(): Promise<WebSearchResult> {
    const url = 'https://www.teletrak.cl/hipismo/carreras';

    const headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'es-CL,es;q=0.9',
        'Cache-Control': 'no-cache',
    };

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000); // 5s máximo

    try {
        // TODO: Evaluar migración a SerpAPI o Browserless para scraping JavaScript-rendered
        const response = await fetch(url, {
            headers,
            signal: controller.signal
        })
        clearTimeout(timeoutId);

        if (!response.ok) {
            return { success: false, data: '', source: 'Teletrak Scraper', error: `HTTP ${response.status}` };
        }

        const html = await response.text()

        // Validación: si el HTML es muy corto, probablemente es un bloqueo o error 403 disfrazado
        if (html.length < 500) {
            return { success: false, data: '', source: 'Teletrak Scraper', error: 'HTML insuficiente (posible bloqueo)' };
        }

        const $ = cheerio.load(html)
        let info = '📡 Información en vivo desde Teletrak.cl:\n'

        $('meta[name="description"]').each((_, el) => {
            info += `Resumen: ${$(el).attr('content')}\n`
        })

        const text = $('body').text()
        if (text.includes('Valparaíso Sporting')) info += "- Valparaíso Sporting: Activo\n"
        if (text.includes('Club Hípico')) info += "- Club Hípico: Activo\n"
        if (text.includes('Hipódromo Chile')) info += "- Hipódromo Chile: Activo\n"

        return { success: true, data: info, source: 'Teletrak Scraper' };

    } catch (e: any) {
        clearTimeout(timeoutId);
        const isTimeout = e.name === 'AbortError';
        console.error('Teletrak Scraping failed:', e.message);
        return {
            success: false,
            data: '',
            source: 'Teletrak Scraper',
            error: isTimeout ? 'Timeout (5s)' : 'Scraping no disponible'
        };
    }
}
