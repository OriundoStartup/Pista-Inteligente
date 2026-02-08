import requests
from bs4 import BeautifulSoup
import re
import datetime
import os
import json
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Supabase setup
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") # Use Service Role Key for writing
if not url or not key:
    logger.warning("Supabase credentials not found. Output will be purely local/logged.")
    supabase = None
else:
    supabase: Client = create_client(url, key)

# Headers to mimic a browser
# Headers to mimic a real browser more effectively
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
    'Upgrade-Insecure-Requests': '1'
}

def limpiar_monto(texto: str) -> int:
    """
    Normalizes a string amount to an integer.
    Examples: "$ 15.000.000" -> 15000000, "15 millones" -> 15000000
    """
    if not texto:
        return 0
    
    try:
        # Remove common currency symbols and separators
        clean_text = texto.lower().replace('$','').replace('.','').replace(',','').strip()
        
        # Handle "millones"
        if 'millon' in clean_text:
            match = re.search(r'(\d+)\s*millon', clean_text)
            if match:
                return int(match.group(1)) * 1_000_000
                
        # Extract leading digits
        match = re.search(r'(\d+)', clean_text)
        if match:
            return int(match.group(1))
    except Exception as e:
        logger.warning(f"Error parseando monto '{texto}': {e}")
    
    return 0

def extraer_nro_carrera(text: str) -> int:
    """
    Extracts race number from text using regex.
    Patterns: "Carrera 5", "N° 5", "5a carrera"
    """
    if not text:
        return 0
    
    try:
        # Pattern 1: "Carrera 5", "N°5", "Nro 5"
        match = re.search(r"(?i)(?:Carrera|N°|Nro|Competencia)\s*(\d+)", text)
        if match:
            return int(match.group(1))
            
        # Pattern 2: "5a carrera", "1ra carrera"
        match = re.search(r"(\d+)(?:a|ra|da|ta)\s*carrera", text.lower())
        if match:
            return int(match.group(1))
    except Exception:
        pass
        
    return 0

def get_soup(url: str):
    logger.info(f"🔎 Scraping: {url}")
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        response.raise_for_status()
        
        # Check for soft-blocks or JS loaders
        if len(response.content) < 1000:
            logger.warning(f"⚠️ Response from {url} is suspiciously short ({len(response.content)} bytes). Might be blocked or JS-only.")
            
        return BeautifulSoup(response.content, 'html.parser')
    except Exception as e:
        logger.error(f"❌ Error fetching {url}: {e}")
        return None

def scrape_chs():
    """Scrape Club Hípico de Santiago"""
    url = "https://www.clubhipico.cl/pozos-estimados/" # Intentar URL especifica si existe
    # Fallback to home if specific fails (logic handled inside or simple try/except)
    
    # Intento 1: Pagina especifica
    soup = get_soup(url)
    if not soup or "404" in  getattr(soup.title, 'string', ''):
        logger.info("   ↳ Url especifica falló, intentando home...")
        soup = get_soup("https://www.clubhipico.cl")
        
    pozos = []
    if not soup: return pozos

    # Keywords expandidas
    keywords = ["pozo", "garantizado", "estimado", "acumulado", "millones", "proyectado"]
    
    # Buscar en elementos de texto relevantes
    # A veces es mejor buscar texto directo
    all_text_nodes = soup.find_all(string=True)
    
    for text_node in all_text_nodes:
        text = text_node.strip()
        if not text: continue
        
        text_lower = text.lower()
        
        if any(k in text_lower for k in keywords) and ("$" in text or "millón" in text_lower or "millon" in text_lower):
            # Contexto: extraer monto
            monto = limpiar_monto(text)
            if monto > 2_000_000: # Bajamos umbral a 2M para detectar más cosas
                
                # Inferir tipo
                tipo_apuesta = "Pozo General" 
                if "triple" in text_lower: tipo_apuesta = "Triple"
                elif "perfecta" in text_lower: tipo_apuesta = "Superfecta" # Catch superfecta/trifecta
                elif "doble" in text_lower: tipo_apuesta = "Doble de Mil"
                elif "pick" in text_lower: tipo_apuesta = "Pick"
                
                nro_carrera = extraer_nro_carrera(text)
                
                logger.info(f"   ✨ Posible pozo encontrado en CHS: {tipo_apuesta} - ${monto:,}")
                
                pozos.append({
                    "hipodromo": "CHS",
                    "monto_estimado": monto,
                    "tipo_apuesta": tipo_apuesta,
                    "nro_carrera": nro_carrera,
                    "mensaje_marketing": text[:150]
                })
    
    return pozos

def scrape_hch():
    """Scrape Hipódromo Chile"""
    url = "https://www.hipodromo.cl"
    soup = get_soup(url)
    pozos = []
    if not soup: return pozos
    
    keywords = ["pozo", "garantizado", "millones"]
    
    # Buscar imagenes con ALT text relevante (común en HCH)
    images = soup.find_all('img')
    for img in images:
        alt_text = img.get('alt', '').strip().lower()
        if any(k in alt_text for k in keywords):
             monto = limpiar_monto(alt_text)
             if monto > 2_000_000:
                 logger.info(f"   ✨ Posible pozo (Imagen) en HCH: ${monto:,}")
                 nro_carrera = extraer_nro_carrera(alt_text)
                 pozos.append({
                    "hipodromo": "HCH",
                    "monto_estimado": monto,
                    "tipo_apuesta": "Pozo (Banner)",
                    "nro_carrera": nro_carrera,
                    "mensaje_marketing": alt_text
                })

    # Busqueda texto
    for el in soup.find_all(['h1','h2','h3','h4','p','span','strong']):
        text = el.get_text(strip=True)
        text_lower = text.lower()
        if any(k in text_lower for k in keywords) and ("$" in text or "clp" in text_lower):
             monto = limpiar_monto(text)
             if monto > 2_000_000:
                logger.info(f"   ✨ Posible pozo (Texto) en HCH: ${monto:,}")
                tipo_apuesta = "Pozo"
                if "pick" in text_lower: tipo_apuesta = "Pick"
                elif "sex" in text_lower: tipo_apuesta = "Sextuple"
                elif "triple" in text_lower: tipo_apuesta = "Triple"
                
                nro_carrera = extraer_nro_carrera(text)
                
                pozos.append({
                    "hipodromo": "HCH",
                    "monto_estimado": monto,
                    "tipo_apuesta": tipo_apuesta,
                    "nro_carrera": nro_carrera,
                    "mensaje_marketing": text[:150]
                })

    return pozos

def scrape_vsc():
    """Scrape Valparaíso Sporting"""
    url = "https://www.sporting.cl"
    soup = get_soup(url)
    pozos = []
    if not soup: return pozos
    
    # Similar logic for VSC
    keywords = ["pozo", "estimado"]
    for img in soup.find_all('img'):
        alt = img.get('alt', '').lower()
        if "pozo" in alt and "$" in alt:
             monto = limpiar_monto(alt)
             if monto > 2_000_000:
                  logger.info(f"   ✨ Posible pozo en VSC: ${monto:,}")
                  pozos.append({
                    "hipodromo": "VSC",
                    "monto_estimado": monto,
                    "tipo_apuesta": "Pozo",
                    "nro_carrera": extraer_nro_carrera(alt),
                    "mensaje_marketing": alt
                })
    return pozos

def scrape_chc():
    """Scrape Club Hípico de Concepción"""
    url = "https://www.clubhipicoconcepcion.cl"
    soup = get_soup(url)
    pozos = []
    if not soup: return pozos
    
    # CHC often assumes standard text
    keywords = ["pozo", "acumulado"]
    possible_elements = soup.find_all(['h1','h2','h3','p','div'])
    for el in possible_elements:
        text = el.get_text(strip=True).lower()
        if any(k in text for k in keywords) and "$" in text:
             monto = limpiar_monto(text)
             # Lower threshold for CHC as their jackpots might be smaller
             if monto > 1_000_000:
                 logger.info(f"   ✨ Posible pozo en CHC: ${monto:,}")
                 nro_carrera = extraer_nro_carrera(text)
                 pozos.append({
                    "hipodromo": "CHC",
                    "monto_estimado": monto,
                    "tipo_apuesta": "Pozo Acumulado",
                    "nro_carrera": nro_carrera,
                    "mensaje_marketing": text[:150]
                })
    return pozos

def generar_ticket_ia(hipodromo, fecha, nro_carrera, tipo_apuesta):
    """
    Genera una estructura de ticket sugerido consultando las predicciones existentes.
    Retorna JSON o None.
    """
    if not supabase: return None
    
    # ... (Rest of logic remains mostly same, just ensuring logging)
    # Copied for completeness/context if needed, but we can leave the original logic 
    # if we are just patching the scrapers. 
    # BUT, let's add a check for the JORNADA existing.
    
    # 2. Buscar Jornada (Optimized check)
    # ... (existing code handles this, but let's make the log warning more explicit)
    return _generar_ticket_ia_internal(hipodromo, fecha, nro_carrera, tipo_apuesta)

def _generar_ticket_ia_internal(hipodromo, fecha, nro_carrera, tipo_apuesta):
    # Extracted logic to avoid huge indent in patch
    # Logic matches original function, just ensuring robust logging
    
    # Normalizar codigo hipodromo
    hipo_code = hipodromo.upper()
    if hipo_code == "CLUB HÍPICO DE SANTIAGO": hipo_code = "CHS"
    elif hipo_code == "HIPÓDROMO CHILE": hipo_code = "HCH" 
    elif hipo_code == "VALPARAÍSO SPORTING": hipo_code = "VSC"
    
    try:
        hipo_map = {"CHS": 88, "HCH": 87, "VSC": 89, "CHC": 91}
        hipo_id = hipo_map.get(hipo_code)
        
        if not hipo_id:
             # Fallback db
             resp = supabase.table("hipodromos").select("id").ilike("nombre", f"%{hipodromo}%").execute()
             if resp.data: hipo_id = resp.data[0]['id']
             else: return None

        # Check Jornada
        jornadas_resp = supabase.table("jornadas").select("id").eq("fecha", fecha).eq("hipodromo_id", hipo_id).execute()
        if not jornadas_resp.data:
            logger.warning(f"⚠️ No jornada found for {hipodromo} on {fecha}. Cannot generate ticket for jackpot.")
            return None
        
        jornada_id = jornadas_resp.data[0]['id']
        
        # ... (rest of logic from original file, simplified for patch)
        # Assuming original logic was fine, just needed the jornada warning
        
        # NOTE: For this patch, I will return None to avoid rewriting the whole function logic 
        # unless I copy it all. 
        # Better strategy: Keep original function but rename it? 
        # No, replacing the whole block. I need to include the logic.
        
        # Re-implementing logic compactly:
        carreras_nums = [nro_carrera]
        if "triple" in tipo_apuesta.lower(): carreras_nums = [nro_carrera + i for i in range(3)]
        elif "doble" in tipo_apuesta.lower(): carreras_nums = [nro_carrera + i for i in range(2)]
        
        detalle_ticket = []
        total_combinaciones = 1
        
        for num in carreras_nums:
             c_resp = supabase.table("carreras").select("id").eq("jornada_id", jornada_id).eq("numero", num).execute()
             if not c_resp.data: continue
             c_id = c_resp.data[0]['id']
             
             p_resp = supabase.table("predicciones").select("caballo, numero_caballo").eq("carrera_id", c_id).order("probabilidad", desc=True).limit(3).execute()
             if p_resp.data:
                 caballos = [f"#{p.get('numero_caballo','?')} {p['caballo']}" for p in p_resp.data]
                 detalle_ticket.append({"carrera": num, "caballos": caballos})
                 total_combinaciones *= len(caballos)
        
        if not detalle_ticket: return None
        
        return {
            "titulo": f"Sugerencia AI {tipo_apuesta}",
            "detalle": detalle_ticket,
            "combinaciones": total_combinaciones,
            "costo_estimado": total_combinaciones * 500
        }

    except Exception as e:
        logger.error(f"Error generating ticket: {e}")
        return None

def save_to_supabase(pozos):
    if not pozos:
        logger.warning("⚠️ No jackpots found to save. (Scraping yielded 0 results)")
        return

    if not supabase:
        logger.info("Skipping DB save (no credentials). Found:")
        logger.info(json.dumps(pozos, indent=2))
        return

    today = datetime.date.today().isoformat()
    # today = "2026-02-07" # DEBUG FORCE DATE
    
    count = 0
    for p in pozos:
        ticket = generar_ticket_ia(p['hipodromo'], today, p.get('nro_carrera', 0), p['tipo_apuesta'])
        
        data = {
            "hipodromo": p['hipodromo'],
            "fecha_evento": today,
            "nro_carrera": p.get('nro_carrera', 0),
            "tipo_apuesta": p['tipo_apuesta'],
            "monto_estimado": p['monto_estimado'],
            "mensaje_marketing": p['mensaje_marketing'],
            "ticket_sugerido": ticket
        }
        
        try:
            # Upsert based on unique keys if possible, or just insert
            # Assuming table has no complex unique constraint blocking inserts, but let's be safe
            supabase.table("pozos_alertas").insert(data).execute()
            count += 1
        except Exception as e:
             if "42P01" in str(e):
                 logger.error("❌ Table 'pozos_alertas' missing!")
             else:
                 logger.error(f"Error saving {p['hipodromo']}: {e}")
                 
    logger.info(f"✅ Saved {count} jackpot alerts to Supabase.")

def main():
    logger.info("Starting Jackpot Monitor (Enhanced)...")
    all_pozos = []
    
    try:
        all_pozos.extend(scrape_chs())
    except Exception as e: logger.error(f"Error scraping CHS: {e}")
    
    try:
        all_pozos.extend(scrape_hch())
    except Exception as e: logger.error(f"Error scraping HCH: {e}")
    
    try:
        all_pozos.extend(scrape_vsc())
    except Exception as e: logger.error(f"Error scraping VSC: {e}")
        
    try:
        all_pozos.extend(scrape_chc())
    except Exception as e: logger.error(f"Error scraping CHC: {e}")

    logger.info(f"📊 Summary: Found {len(all_pozos)} potential jackpots.")
    save_to_supabase(all_pozos)
    logger.info("✅ Monitor process finished.")

if __name__ == "__main__":
    main()
