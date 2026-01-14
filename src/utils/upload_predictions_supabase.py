"""
Upload Predictions to Supabase
Reads predictions from JSON/SQLite and uploads to Supabase 'predicciones' table.

Author: ML Engineering Team
Date: 2026-01-14
"""

import os
import sys
import json
import logging
from datetime import datetime
import pandas as pd

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
        
        if not hip_res.data:
            # Try common variations
            hip_res = client.table('hipodromos').select('id').ilike('nombre', f'%{hipodromo.split()[0]}%').execute()
        
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
            return car_res.data[0]['id']
        else:
            # Create carrera
            logger.info(f"   🆕 Creating carrera: C{nro_carrera}")
            insert_res = client.table('carreras').insert({
                'jornada_id': jor_id,
                'numero': nro_carrera
            }).execute()
            if insert_res.data:
                return insert_res.data[0]['id']
            else:
                logger.error(f"   ❌ Failed to create carrera")
                return None
        
    except Exception as e:
        logger.error(f"Error resolving/creating carrera_id: {e}")
        return None


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
        
        # Insert batch
        try:
            result = client.table('predicciones').insert(records).execute()
            if result.data:
                uploaded_count += len(records)
                logger.info(f"   ✅ Uploaded {len(records)} predictions for C{nro_carrera}")
        except Exception as e:
            logger.error(f"   ❌ Error uploading predictions for {race_key}: {e}")
            failed_races.append(race_key)
    
    if failed_races:
        logger.warning(f"⚠️ Failed to upload {len(failed_races)} races: {failed_races[:5]}...")
    
    return uploaded_count


def run_upload():
    """Main function to upload predictions"""
    logger.info("=" * 60)
    logger.info("📤 UPLOAD PREDICTIONS TO SUPABASE")
    logger.info("=" * 60)
    
    # Load predictions
    predictions = load_predictions()
    
    if not predictions:
        logger.warning("No predictions to upload. Run inference first.")
        return 0
    
    # Upload
    count = upload_predictions_to_supabase(predictions)
    
    logger.info("=" * 60)
    logger.info(f"✅ Uploaded {count} predictions to Supabase")
    logger.info("=" * 60)
    
    return count


if __name__ == "__main__":
    run_upload()
