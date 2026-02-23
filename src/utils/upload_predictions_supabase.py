"""
Upload Predictions to Supabase (v2.0 - With Retry Logic)
Reads predictions from JSON/SQLite and uploads to Supabase 'predicciones' table.
Includes automatic retry on failures and post-upload verification.

Author: ML Engineering Team
Date: 2026-02-10
"""

import os
import sys
import json
import logging
from datetime import datetime
import pandas as pd
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.utils.supabase_client import SupabaseManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

JSON_PATH = 'data/predicciones_activas.json'


def load_predictions():
    """Load predictions from JSON file"""
    if not os.path.exists(JSON_PATH):
        logger.error(f"❌ Predictions file not found: {JSON_PATH}")
        return []
    
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        predictions = json.load(f)
    
    logger.info(f"📥 Loaded {len(predictions)} predictions from {JSON_PATH}")
    return predictions


def resolve_carrera_id(db, hipodromo: str, fecha: str, nro_carrera: int) -> str:
    """
    Resolve carrera_id from hipodromo + fecha + nro_carrera.
    Creates hipodromo, jornada, carrera if they don't exist.
    Returns carrera_id (UUID) or None if failed.
    """
    try:
        client = db.get_client()
        if not client:
            return None
        
        # === STEP 1: Resolve/Create Hipodromo ===
        hip_res = client.table('hipodromos').select('id').eq('nombre', hipodromo).execute()
        
        # [FIX] Removed unsafe fuzzy matching (Club -> Club Hipico de Santiago)
        # if not hip_res.data:
        #    hip_res = client.table('hipodromos').select('id').ilike('nombre', f'%{hipodromo.split()[0]}%').execute()
        
        if hip_res.data:
            hip_id = hip_res.data[0]['id']
        else:
            # Create hipodromo
            logger.info(f"   🆕 Creating hipodromo: {hipodromo}")
            insert_res = client.table('hipodromos').insert({'nombre': hipodromo}).execute()
            if insert_res.data:
                hip_id = insert_res.data[0]['id']
            else:
                logger.error(f"   ❌ Failed to create hipodromo: {hipodromo}")
                return None
        
        # === STEP 2: Resolve/Create Jornada ===
        jor_res = client.table('jornadas').select('id').eq('hipodromo_id', hip_id).eq('fecha', fecha).execute()
        
        if jor_res.data:
            jor_id = jor_res.data[0]['id']
        else:
            # Create jornada
            logger.info(f"   🆕 Creating jornada: {hipodromo} {fecha}")
            insert_res = client.table('jornadas').insert({
                'hipodromo_id': hip_id,
                'fecha': fecha
            }).execute()
            if insert_res.data:
                jor_id = insert_res.data[0]['id']
            else:
                logger.error(f"   ❌ Failed to create jornada")
                return None
        
        # === STEP 3: Resolve/Create Carrera ===
        car_res = client.table('carreras').select('id').eq('jornada_id', jor_id).eq('numero', nro_carrera).execute()
        
        if car_res.data:
            carrera_id = car_res.data[0]['id']
            
            # Check if we need to update hora/distancia (might be empty)
            car_full = client.table('carreras').select('hora, distancia').eq('id', carrera_id).execute()
            if car_full.data and (not car_full.data[0].get('hora') or not car_full.data[0].get('distancia')):
                # Try to get from programa_carreras
                hora, distancia = get_hora_distancia_from_sqlite(fecha, hipodromo, nro_carrera)
                if hora or distancia:
                    update_data = {}
                    if hora:
                        update_data['hora'] = hora
                    if distancia:
                        update_data['distancia'] = distancia
                    client.table('carreras').update(update_data).eq('id', carrera_id).execute()
                    logger.info(f"   📝 Updated carrera C{nro_carrera} with hora={hora}, distancia={distancia}")
            
            return carrera_id
        else:
            # Get hora and distancia from programa_carreras (SQLite)
            hora, distancia = get_hora_distancia_from_sqlite(fecha, hipodromo, nro_carrera)
            
            # Create carrera with hora and distancia
            logger.info(f"   🆕 Creating carrera: C{nro_carrera} (hora={hora}, dist={distancia})")
            insert_res = client.table('carreras').insert({
                'jornada_id': jor_id,
                'numero': nro_carrera,
                'hora': hora,
                'distancia': distancia
            }).execute()
            if insert_res.data:
                return insert_res.data[0]['id']
            else:
                logger.error(f"   ❌ Failed to create carrera")
                return None
        
    except Exception as e:
        logger.error(f"Error resolving/creating carrera_id: {e}")
        return None


def get_hora_distancia_from_sqlite(fecha: str, hipodromo: str, nro_carrera: int):
    """
    Read hora and distancia from programa_carreras SQLite table.
    Returns (hora, distancia) tuple.
    """
    import sqlite3
    
    DB_PATH = 'data/db/hipica_data.db'
    hora = None
    distancia = None
    
    try:
        if not os.path.exists(DB_PATH):
            return (None, None)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Query programa_carreras for hora and distancia
        cursor.execute("""
            SELECT hora, distancia 
            FROM programa_carreras 
            WHERE fecha = ? AND hipodromo LIKE ? AND nro_carrera = ?
            LIMIT 1
        """, (fecha, f'%{hipodromo.split()[0]}%', nro_carrera))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            hora = result[0]
            # Clean hora (remove "APROX." etc.)
            if hora:
                hora = hora.replace('APROX.', '').replace('aprox.', '').strip()
            
            # Parse distancia to integer
            if result[1]:
                try:
                    distancia = int(str(result[1]).replace('m', '').replace('M', '').strip())
                except:
                    distancia = None
                    
        return (hora, distancia)
        
    except Exception as e:
        logger.warning(f"Could not read hora/distancia from SQLite: {e}")
        return (None, None)


def upload_predictions_to_supabase(predictions: list) -> int:
    """
    Upload predictions to Supabase 'predicciones' table.
    Returns number of successfully uploaded predictions.
    """
    if not predictions:
        logger.warning("⚠️ No predictions to upload")
        return 0
    
    db = SupabaseManager()
    client = db.get_client()
    
    if not client:
        logger.error("❌ Supabase client not available")
        return 0
    
    # Group predictions by carrera for ranking
    df = pd.DataFrame(predictions)
    
    if df.empty:
        return 0
    
    # Create unique race identifier
    df['race_key'] = df['fecha'] + '_' + df['hipodromo'] + '_' + df['carrera'].astype(str)
    
    uploaded_count = 0
    failed_races = []
    
    # Process by race
    for race_key, group in df.groupby('race_key'):
        # Parse race info
        parts = race_key.split('_')
        fecha = parts[0]
        hipodromo = '_'.join(parts[1:-1])  # Handle names with underscores
        nro_carrera = int(parts[-1])
        
        # Resolve carrera_id
        carrera_id = resolve_carrera_id(db, hipodromo, fecha, nro_carrera)
        
        if not carrera_id:
            failed_races.append(race_key)
            continue
        
        # Sort by probability for ranking
        group_sorted = group.sort_values('probabilidad', ascending=False).reset_index(drop=True)
        
        # Delete existing predictions for this carrera (to avoid duplicates)
        try:
            client.table('predicciones').delete().eq('carrera_id', carrera_id).execute()
        except Exception as e:
            logger.warning(f"   Could not delete old predictions: {e}")
        
        # Prepare records
        records = []
        for rank, (_, row) in enumerate(group_sorted.iterrows(), 1):
            record = {
                'carrera_id': carrera_id,
                'numero_caballo': int(row['numero']) if pd.notna(row['numero']) else 0,
                'caballo': str(row['caballo']),
                'jinete': str(row.get('jinete', '')),
                'probabilidad': float(row['probabilidad']) / 100.0,  # Store as 0-1
                'rank_predicho': rank,
                'modelo_version': 'ensemble_v4'
            }
            records.append(record)
        
        # Insert batch with retry
        try:
            result = upload_batch_with_retry(client, records)
            if result.data:
                uploaded_count += len(records)
                logger.info(f"   ✅ Uploaded {len(records)} predictions for C{nro_carrera}")
        except Exception as e:
            logger.error(f"   ❌ Error uploading predictions for {race_key} after retries: {e}")
            failed_races.append(race_key)
    
    if failed_races:
        logger.warning(f"⚠️ Failed to upload {len(failed_races)} races: {failed_races[:5]}...")
    
    return uploaded_count


@retry(
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type((ConnectionError, TimeoutError, Exception)),
    reraise=True
)
def upload_batch_with_retry(client, records):
    """Upload a batch of predictions with automatic retry on failure."""
    logger.debug(f"   Attempting upload of {len(records)} records...")
    return client.table('predicciones').insert(records).execute()


def verify_upload(client, expected_races, fecha_inicio):
    """
    Verify that predictions were uploaded correctly.
    Returns True if verification passes.
    """
    try:
        # Count predictions uploaded since fecha_inicio
        result = client.table('predicciones').select(
            'id,carreras!inner(jornadas!inner(fecha))'
        ).gte('carreras.jornadas.fecha', fecha_inicio).execute()
        
        uploaded_count = len(result.data or [])
        
        logger.info(f"\n📊 Verificación:")
        logger.info(f"   Predicciones en Supabase (desde {fecha_inicio}): {uploaded_count}")
        logger.info(f"   Carreras esperadas: {expected_races}")
        
        # Check if we have reasonable coverage
        if uploaded_count > 0:
            logger.info(f"   ✅ Upload verificado exitosamente")
            return True
        else:
            logger.warning(f"   ⚠️ No se encontraron predicciones en Supabase")
            return False
            
    except Exception as e:
        logger.error(f"   ❌ Error en verificación: {e}")
        return False


def run_upload():
    """Main function to upload predictions with verification"""
    logger.info("=" * 60)
    logger.info("📤 UPLOAD PREDICTIONS TO SUPABASE (v2.0 - With Retry)")
    logger.info("=" * 60)
    
    # Load predictions
    predictions = load_predictions()
    
    if not predictions:
        logger.warning("No predictions to upload. Run inference first.")
        return 0
    
    # Get fecha range for verification
    df = pd.DataFrame(predictions)
    fecha_inicio = df['fecha'].min()
    num_races = len(df.groupby(['fecha', 'hipodromo', 'carrera']))
    
    logger.info(f"\nPreparando upload:")
    logger.info(f"   Total predicciones: {len(predictions)}")
    logger.info(f"   Carreras: {num_races}")
    logger.info(f"   Fecha inicio: {fecha_inicio}")
    
    # Upload
    count = upload_predictions_to_supabase(predictions)
    
    # Verify
    db = SupabaseManager()
    client = db.get_client()
    
    if client:
        verify_upload(client, num_races, fecha_inicio)
    
    logger.info("\n" + "=" * 60)
    logger.info(f"✅ Upload completado: {count} predicciones")
    logger.info("=" * 60)
    
    return count


if __name__ == "__main__":
    run_upload()
