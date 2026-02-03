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
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def limpiar_monto(texto: str) -> int:
    """
    Normalizes a string amount to an integer.
    Examples: "$ 15.000.000" -> 15000000, "15 millones" -> 15000000
    """
    if not texto:
        return 0
    
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
    
    return 0

def get_soup(url: str):
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        return None

def scrape_chs():
    """Scrape Club Hípico de Santiago"""
    url = "https://www.clubhipico.cl"
    soup = get_soup(url)
    pozos = []
    if not soup: return pozos

    # Example logic - selector needs adjustment based on real site structure
    # Looking for "Pozos" or "Estimados"
    # CHS usually has a section for 'Pozos Estimados'
    
    # Generic search for keywords in text if specific selectors fail or are unknown
    keywords = ["pozo", "garantizado", "estimado", "acumulado"]
    
    # Find containers that might hold this info
    # This is a heuristic approach since we don't have the live site DOM
    possible_elements = soup.find_all(['div', 'span', 'p', 'h1', 'h2', 'h3'])
    
    for el in possible_elements:
        text = el.get_text(strip=True).lower()
        if any(k in text for k in keywords) and "$" in text:
            # Try to extract the closest amount
            monto = limpiar_monto(text)
            if monto > 5_000_000:
                # Try to infer bet type context from parent or siblings
                tipo_apuesta = "Pozo General" # Default
                if "triple" in text: tipo_apuesta = "Triple"
                elif "superfecta" in text: tipo_apuesta = "Superfecta"
                elif "doble" in text: tipo_apuesta = "Doble de Mil"
                
                pozos.append({
                    "hipodromo": "CHS",
                    "monto_estimado": monto,
                    "tipo_apuesta": tipo_apuesta,
                    "mensaje_marketing": text[:100] # Capture a snippet
                })
    return pozos

def scrape_hch():
    """Scrape Hipódromo Chile"""
    url = "https://www.hipodromo.cl"
    soup = get_soup(url)
    pozos = []
    if not soup: return pozos
    
    # HCH often puts popups or banners. 
    # Check for specific classes or IDs if known, otherwise generic keyword search
    keywords = ["pozo", "garantizado"]
    
    possible_elements = soup.find_all(['div', 'a', 'span'])
    for el in possible_elements:
        text = el.get_text(strip=True).lower()
        if any(k in text for k in keywords) and ("$" in text or "clp" in text):
             monto = limpiar_monto(text)
             if monto > 5_000_000:
                tipo_apuesta = "Pozo"
                if "pick" in text: tipo_apuesta = "Pick"
                elif "sex" in text: tipo_apuesta = "Sextuple" # Careful with substring matching!
                elif "sextu" in text: tipo_apuesta = "Sextuple"
                
                pozos.append({
                    "hipodromo": "HCH",
                    "monto_estimado": monto,
                    "tipo_apuesta": tipo_apuesta,
                    "mensaje_marketing": text[:100]
                })
    return pozos

def scrape_vsc():
    """Scrape Valparaíso Sporting"""
    url = "https://www.sporting.cl"
    soup = get_soup(url)
    pozos = []
    if not soup: return pozos
    
    # Sporting is often image based or within an slider
    # Look for 'alt' text in images or specific promotional divs
    images = soup.find_all('img')
    for img in images:
        alt_text = img.get('alt', '').lower()
        if "pozo" in alt_text and "$" in alt_text:
             monto = limpiar_monto(alt_text)
             if monto > 5_000_000:
                 pozos.append({
                    "hipodromo": "VSC",
                    "monto_estimado": monto,
                    "tipo_apuesta": "Pozo (Banner)",
                    "mensaje_marketing": alt_text
                })
                 
    # Also check text
    # ... logic similar to others ...
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
             if monto > 5_000_000:
                 pozos.append({
                    "hipodromo": "CHC",
                    "monto_estimado": monto,
                    "tipo_apuesta": "Pozo Acumulado",
                    "mensaje_marketing": text[:100]
                })
    return pozos

def save_to_supabase(pozos):
    if not pozos:
        logger.info("No updated jackpots found.")
        return

    if not supabase:
        logger.info("Skipping DB save (no credentials). Found:")
        logger.info(json.dumps(pozos, indent=2))
        return

    today = datetime.date.today().isoformat()
    
    for p in pozos:
        # Check if exists to avoid duplicates for same day/race/type
        # For now, simple insert. RLS handles auth.
        # We might want to deduplicate based on day + hipodromo + tipo_apuesta
        # But allow updates? Let's just insert for log history or upsert if we had a unique key.
        # Since we don't have a unique constraint on (date, hipodromo, type) in the create script yet (only index),
        # we will just insert.
        
        data = {
            "hipodromo": p['hipodromo'],
            "fecha_evento": today, # Assuming the pozo is for the next event or today. 
            "nro_carrera": 0, # Default 0 if unknown
            "tipo_apuesta": p['tipo_apuesta'],
            "monto_estimado": p['monto_estimado'],
            "mensaje_marketing": p['mensaje_marketing']
        }
        
        try:
            supabase.table("pozos_alertas").insert(data).execute()
            logger.info(f"Saved alert: {p['hipodromo']} - {p['monto_estimado']}")
        except Exception as e:
            error_msg = str(e)
            if "relation \"pozos_alertas\" does not exist" in error_msg or "42P01" in error_msg:
                logger.error("❌ ERROR CRÍTICO: La tabla 'pozos_alertas' no existe en Supabase.")
                logger.error("👉 Por favor ejecuta el script 'src/sql/00_create_pozos_alertas.sql' en el Editor SQL de Supabase.")
            else:
                logger.error(f"Error saving to DB: {e}")

def main():
    logger.info("Starting Jackpot Monitor...")
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

    logger.info(f"Found {len(all_pozos)} potential jackpots.")
    save_to_supabase(all_pozos)
    logger.info("Done.")

if __name__ == "__main__":
    main()
