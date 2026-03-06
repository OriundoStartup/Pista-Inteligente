import * as cheerio from 'cheerio'

const SERPER_API_KEY = process.env.SERPER_API_KEY
const EXTERNAL_LINKS = `
- Teletrak: https://www.teletrak.cl/
- Club Hípico de Santiago: https://www.clubhipico.cl/
- Hipódromo Chile: https://www.hipodromo.cl/
- Valparaíso Sporting: https://www.sporting.cl/
`

const TELETRAK_URLS = {
    carreras: 'https://www.teletrak.cl/hipismo/carreras',
    programas: 'https://www.teletrak.cl/hipismo/programas',
    calendario: 'https://www.teletrak.cl/hipismo/calendario'
}

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
    // Intentamos primero con programas ya que suele tener más detalle estructurado
    const urlsToTry = [TELETRAK_URLS.programas, TELETRAK_URLS.carreras];
    let combinedInfo = '📡 Información recuperada de Teletrak.cl:\n';
    let sourceFound = false;

    const headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'es-CL,es;q=0.9',
        'Cache-Control': 'no-cache',
    };

    for (const url of urlsToTry) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 4000); // 4s por URL

        try {
            const response = await fetch(url, { headers, signal: controller.signal });
            clearTimeout(timeoutId);

            if (!response.ok) continue;

            const html = await response.text();
            if (html.length < 500) continue;

            const $ = cheerio.load(html);
            sourceFound = true;

            // Intentar extraer descripción meta
            const metaDesc = $('meta[name="description"]').attr('content');
            if (metaDesc && !combinedInfo.includes(metaDesc)) combinedInfo += `Contexto: ${metaDesc}\n`;

            // Buscar tablas de programación o listas de carreras
            $('table, .program-list, .race-entry, .row').each((_, el) => {
                const text = $(el).text().trim().replace(/\s\s+/g, ' ');
                // Filtramos por palabras clave para no traer ruido excesivo
                if (text.includes('Carrera') || text.includes('Hipódromo') || text.includes('Hora')) {
                    if (text.length > 20 && text.length < 400) {
                        if (!combinedInfo.includes(text.substring(0, 50))) { // Evitar duplicados exactos
                            combinedInfo += `- ${text}\n`;
                        }
                    }
                }
            });

            // Si ya encontramos datos representativos decentes, paramos para no saturar el prompt
            if (combinedInfo.length > 600) break;

        } catch (e) {
            clearTimeout(timeoutId);
            console.error(`Error scraping ${url}:`, e);
        }
    }

    if (!sourceFound || combinedInfo.length < 50) {
        return {
            success: false,
            data: combinedInfo + 'No se pudo extraer detalle estructurado del programa.',
            source: 'Teletrak Scraper',
            error: 'Contenido dinámico o bloqueo de scraping'
        };
    }

    return { success: true, data: combinedInfo, source: 'Teletrak Scraper' };
}
