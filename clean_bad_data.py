
import os
import sys
import logging
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from src.utils.supabase_client import SupabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Cleaner")

def clean_bad_data():
    load_dotenv()
    db = SupabaseManager()
    client = db.get_client()
    
    if not client:
        logger.error("No Supabase client")
        return

    # 1. Identify "Club Hípico de Santiago" (ID 1 usually, but let's check)
    res = client.table('hipodromos').select('id').eq('nombre', 'Club Hípico de Santiago').execute()
    if not res.data:
        logger.warning("Club Hípico de Santiago not found")
        return
    chs_id = res.data[0]['id']
    logger.info(f"Targeting CHS ID: {chs_id}")

    # 2. Find Jornada for 2026-02-03 at CHS
    target_date = '2026-02-03'
    
    jornadas = client.table('jornadas').select('id').eq('hipodromo_id', chs_id).eq('fecha', target_date).execute()
    
    if not jornadas.data:
        logger.info("✅ No bad jornadas found for 2026-02-03 at CHS.")
        return

    for j in jornadas.data:
        jid = j['id']
        logger.info(f"🗑️ Deleting bad jornada {jid}...")
        
        # Cascade delete (manually if needed, but Supabase might handle it)
        # Delete Carreras first to be safe
        carreras = client.table('carreras').select('id').eq('jornada_id', jid).execute()
        for c in (carreras.data or []):
            cid = c['id']
            # Delete Predicciones
            client.table('predicciones').delete().eq('carrera_id', cid).execute()
            # Delete Participaciones
            client.table('participaciones').delete().eq('carrera_id', cid).execute()
            
            client.table('carreras').delete().eq('id', cid).execute()
        
        # Delete Jornada
        client.table('jornadas').delete().eq('id', jid).execute()
        
    logger.info("✅ Cleanup complete.")

if __name__ == "__main__":
    clean_bad_data()
