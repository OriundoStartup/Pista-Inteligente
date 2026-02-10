import os
import sys
import sqlite3
import json
import logging
from datetime import datetime

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.utils.supabase_client import SupabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = 'data/db/hipica_data.db'

def backfill_predictions():
    logger.info("Starting backfill of predictions from Supabase to SQLite...")
    
    db = SupabaseManager()
    client = db.get_client()
    
    if not client:
        logger.error("Supabase client not available")
        return

    # Fetch 2026 predictions
    logger.info("Fetching 2026 predictions from Supabase...")
    try:
        # Join with carreras -> jornadas to filter by date
        # Note: Supabase-js select syntax for joins is specific. 
        # Easier to fetch flat if possible, or filter in python if volume is low.
        # Let's try fetching distinct race_ids first or just date filter if we added date to predictions (we didn't).
        # We'll rely on created_at or fetch via join.
        
        # Actually, let's fetch all predictions created > 2026-01-01.
        # Assuming created_at roughly matches race date for active predictions.
        res = client.table('predicciones') \
            .select('*, carreras(jornadas(fecha, hipodromos(nombre)), numero)') \
            .gte('created_at', '2026-01-01T00:00:00') \
            .execute()
            
        preds = res.data
        logger.info(f"Fetched {len(preds)} predictions.")
        
    except Exception as e:
        logger.error(f"Error fetching from Supabase: {e}")
        return

    if not preds:
        logger.info("No predictions found.")
        return

    # Prepare for SQLite insertion
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Ensure tables exist (mimic structure needed by calculate_performance)
    # calculate_performance uses: 
    # predicciones(fecha_carrera, hipodromo, nro_carrera, numero_caballo, ranking_prediccion, caballo_id, metadata)
    
    # We might need to recreate table or alert if schema mismatches.
    # Let's assume schema exists or we create it.
    
    count = 0
    for p in preds:
        try:
            # Extract joined data
            carrera = p.get('carreras') or {}
            jornada = carrera.get('jornadas') or {}
            hipodromo_obj = jornada.get('hipodromos') or {}
            
            fecha = jornada.get('fecha')
            hipodromo = hipodromo_obj.get('nombre')
            nro_carrera = carrera.get('numero')
            
            if not fecha or not hipodromo or not nro_carrera:
                continue
                
            # Prepare metadata
            metadata = json.dumps({'caballo': p.get('caballo'), 'jinete': p.get('jinete')})
            
            # Map basic columns
            # Note: IDs (caballo_id) might not match between Supabase and Local if they aren't synced perfectly.
            # calculate_performance uses joins on names often or relies on standardized IDs.
            # Let's check calculate_performance query:
            # INNER JOIN hipodromos h ON j.hipodromo_id = h.id AND h.nombre = p.hipodromo
            # It joins PREDICTIONS on (fecha_carrera, hipodromo, nro_carrera).
            # It gets result from PARTICIPACIONES.
            
            # We need to insert into 'predicciones' table.
            # Schema usually: id, fecha_carrera, hipodromo, nro_carrera, numero_caballo, ...
            
            cursor.execute("""
                INSERT OR IGNORE INTO predicciones 
                (fecha_carrera, hipodromo, nro_carrera, numero_caballo, ranking_prediccion, caballo_id, metadata, puntaje_ia, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                fecha,
                hipodromo,
                nro_carrera,
                p.get('numero_caballo'),
                p.get('rank_predicho'),
                0, # caballo_id - might be unknown locally, relying on number/name match
                metadata,
                p.get('probabilidad'),
                p.get('created_at')
            ))
            count += 1
            
        except Exception as e:
            logger.warning(f"Error inserting row: {e}")

    conn.commit()
    conn.close()
    logger.info(f"Successfully backfilled {count} predictions to SQLite.")

if __name__ == "__main__":
    backfill_predictions()
