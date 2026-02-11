"""
Calculate Performance Metrics: Compares predictions vs actual results.
Calculates: Ganador Exacto, Quiniela, Trifecta, Superfecta

UPDATED: Now reads predictions from Supabase with proper joins.

Author: ML Engineering Team
Date: 2026-02-07
"""

import sqlite3
import os
import sys
import json
import logging
from datetime import datetime, timedelta
from collections import defaultdict

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.utils.supabase_client import SupabaseManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_PATH = 'data/db/hipica_data.db'


def get_predictions_from_supabase():
    """
    Fetch all predictions from Supabase with race info.
    Returns dict keyed by (fecha, hipodromo, nro_carrera) -> list of predictions.
    Uses manual pagination to overcome Supabase's 1000 record limit.
    """
    try:
        db = SupabaseManager()
        client = db.get_client()
        if not client:
            logger.warning("Supabase client not available")
            return {}
        
        # Manual pagination to fetch all predictions
        all_preds = []
        batch_size = 1000
        offset = 0
        
        while True:
            # Fetch batch with pagination using range()
            result = client.table('predicciones').select(
                '*,'
                'carreras!inner(numero, jornadas!inner(fecha, hipodromos!inner(nombre)))'
            ).range(offset, offset + batch_size - 1).execute()
            
            batch = result.data if result.data else []
            if not batch:
                break  # No more data
            
            all_preds.extend(batch)
            logger.info(f"Fetched batch: {len(batch)} predictions (total so far: {len(all_preds)})")
            
            if len(batch) < batch_size:
                break  # Last batch (less than 1000 records)
            
            offset += batch_size
        
        logger.info(f"Total predictions fetched: {len(all_preds)}")
        
        # Group by race
        by_race = defaultdict(list)
        for p in all_preds:
            carrera = p.get('carreras', {})
            jornada = carrera.get('jornadas', {})
            hipodromo = jornada.get('hipodromos', {})
            
            fecha = jornada.get('fecha')
            hip_nombre = hipodromo.get('nombre')
            nro_carrera = carrera.get('numero')
            
            if not fecha or not hip_nombre or not nro_carrera:
                continue
            
            key = (fecha, hip_nombre, nro_carrera)
            by_race[key].append({
                'caballo': p.get('caballo'),
                'numero_caballo': p.get('numero_caballo'),
                'rank_predicho': p.get('rank_predicho'),
                'probabilidad': p.get('probabilidad')
            })
        
        # Sort each race's predictions by ranking
        for key in by_race:
            by_race[key].sort(key=lambda x: x.get('rank_predicho') or 999)
        
        logger.info(f"Grouped into {len(by_race)} races")
        return by_race
        
    except Exception as e:
        logger.error(f"Error fetching predictions from Supabase: {e}")
        import traceback
        traceback.print_exc()
        return {}


def get_results_from_sqlite():
    """
    Get actual race results from SQLite.
    Returns dict keyed by (fecha, hipodromo, nro_carrera) -> list of top 4 finishers.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all races with results
    query = """
    SELECT 
        j.fecha,
        h.nombre as hipodromo,
        c.numero as nro_carrera,
        part.posicion,
        part.caballo_id,
        cab.nombre as caballo_nombre
    FROM participaciones part
    INNER JOIN carreras c ON part.carrera_id = c.id
    INNER JOIN jornadas j ON c.jornada_id = j.id
    INNER JOIN hipodromos h ON j.hipodromo_id = h.id
    INNER JOIN caballos cab ON part.caballo_id = cab.id
    WHERE part.posicion IS NOT NULL AND part.posicion > 0 AND part.posicion <= 4
    ORDER BY j.fecha DESC, h.nombre, c.numero, part.posicion
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    
    # Group by race
    by_race = defaultdict(list)
    for row in rows:
        key = (row['fecha'], row['hipodromo'], row['nro_carrera'])
        by_race[key].append({
            'posicion': row['posicion'],
            'caballo_id': row['caballo_id'],
            'caballo_nombre': row['caballo_nombre']
        })
    
    # Sort each race by position
    for key in by_race:
        by_race[key].sort(key=lambda x: x['posicion'])
    
    logger.info(f"Fetched results for {len(by_race)} races from SQLite")
    return by_race


def normalize_name(name):
    """Normalize horse name for comparison."""
    if not name:
        return ""
    return name.upper().strip()


def match_predictions_with_results(predictions_by_race, results_by_race):
    """
    Match predictions with results and calculate hits.
    """
    results = []
    
    for key, preds in predictions_by_race.items():
        fecha, hipodromo, nro_carrera = key
        
        if key not in results_by_race:
            continue  # No results for this race yet
        
        actual = results_by_race[key]
        if len(actual) < 1 or len(preds) < 1:
            continue
        
        # Extract top 4 predictions
        pred_top4 = preds[:4]
        pred_nombres = [normalize_name(p.get('caballo')) for p in pred_top4]
        
        # Get actual results
        actual_nombres = [normalize_name(a.get('caballo_nombre')) for a in actual[:4]]
        
        # Calculate hits using normalized names
        ganador_exacto = len(pred_nombres) > 0 and len(actual_nombres) > 0 and pred_nombres[0] == actual_nombres[0]
        
        # Quiniela: Top 2 preds match actual 1st and 2nd in EXACT ORDER
        quiniela = False
        if len(pred_nombres) >= 2 and len(actual_nombres) >= 2:
            quiniela = pred_nombres[:2] == actual_nombres[:2]
        
        # Trifecta: Top 3 preds match actual 1st, 2nd, 3rd in EXACT ORDER
        trifecta = False
        if len(pred_nombres) >= 3 and len(actual_nombres) >= 3:
            trifecta = pred_nombres[:3] == actual_nombres[:3]
        
        # Superfecta: Top 4 preds match actual 1st, 2nd, 3rd, 4th in EXACT ORDER
        superfecta = False
        if len(pred_nombres) >= 4 and len(actual_nombres) >= 4:
            superfecta = pred_nombres[:4] == actual_nombres[:4]
        
        # Get display names (original case)
        pred_display = [p.get('caballo', '') for p in pred_top4]
        actual_display = [a.get('caballo_nombre', '') for a in actual[:4]]
        
        results.append({
            'fecha': fecha,
            'hipodromo': hipodromo,
            'nro_carrera': nro_carrera,
            'acierto_ganador': ganador_exacto,
            'acierto_quiniela': quiniela,
            'acierto_trifecta': trifecta,
            'acierto_superfecta': superfecta,
            'prediccion_top4': pred_display,
            'resultado_top4': actual_display
        })
    
    return results


def calculate_stats(results, days=None):
    """Calculate aggregate stats from results, optionally filtered by days."""
    if days:
        cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        results = [r for r in results if r['fecha'] >= cutoff]
    
    if not results:
        return {
            'total_carreras': 0,
            'ganador_pct': 0,
            'quiniela_pct': 0,
            'trifecta_pct': 0,
            'superfecta_pct': 0,
            'ganador_count': 0,
            'quiniela_count': 0,
            'trifecta_count': 0,
            'superfecta_count': 0
        }
    
    total = len(results)
    ganador = sum(1 for r in results if r['acierto_ganador'])
    quiniela = sum(1 for r in results if r['acierto_quiniela'])
    trifecta = sum(1 for r in results if r['acierto_trifecta'])
    superfecta = sum(1 for r in results if r['acierto_superfecta'])
    
    return {
        'total_carreras': total,
        'ganador_pct': round((ganador / total) * 100, 1) if total > 0 else 0,
        'quiniela_pct': round((quiniela / total) * 100, 1) if total > 0 else 0,
        'trifecta_pct': round((trifecta / total) * 100, 1) if total > 0 else 0,
        'superfecta_pct': round((superfecta / total) * 100, 1) if total > 0 else 0,
        'ganador_count': ganador,
        'quiniela_count': quiniela,
        'trifecta_count': trifecta,
        'superfecta_count': superfecta
    }


def calculate_stats_by_hipodromo(results):
    """Group results by hipodromo and calculate stats for each."""
    by_hip = defaultdict(list)
    for r in results:
        by_hip[r['hipodromo']].append(r)
    
    return {hip: calculate_stats(races) for hip, races in by_hip.items()}


def save_to_sqlite(results):
    """Save results to SQLite table rendimiento_historico."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rendimiento_historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            hipodromo TEXT NOT NULL,
            nro_carrera INTEGER NOT NULL,
            acierto_ganador BOOLEAN,
            acierto_quiniela BOOLEAN,
            acierto_trifecta BOOLEAN,
            acierto_superfecta BOOLEAN,
            prediccion_top4 TEXT,
            resultado_top4 TEXT,
            UNIQUE(fecha, hipodromo, nro_carrera)
        )
    ''')
    
    # Insert or replace
    for r in results:
        cursor.execute('''
            INSERT OR REPLACE INTO rendimiento_historico 
            (fecha, hipodromo, nro_carrera, acierto_ganador, acierto_quiniela, 
             acierto_trifecta, acierto_superfecta, prediccion_top4, resultado_top4)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            r['fecha'], r['hipodromo'], r['nro_carrera'],
            r['acierto_ganador'], r['acierto_quiniela'],
            r['acierto_trifecta'], r['acierto_superfecta'],
            json.dumps(r['prediccion_top4'], ensure_ascii=False),
            json.dumps(r['resultado_top4'], ensure_ascii=False)
        ))
    
    conn.commit()
    conn.close()
    logger.info(f"Saved {len(results)} records to rendimiento_historico")


def save_stats_json(stats_global, stats_by_hip, recent_results):
    """Save stats to JSON for frontend consumption."""
    output = {
        'generated_at': datetime.now().isoformat(),
        'global': {
            'last_30_days': calculate_stats(recent_results, days=30),
            'last_90_days': calculate_stats(recent_results, days=90),
            'all_time': stats_global
        },
        'by_hipodromo': stats_by_hip,
        'recent_races': recent_results[:50]
    }
    
    os.makedirs('data', exist_ok=True)
    with open('data/rendimiento_stats.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    logger.info("Saved stats to data/rendimiento_stats.json")


def upload_to_supabase(stats_global, stats_by_hip, all_results):
    """Upload stats to Supabase for frontend."""
    try:
        db = SupabaseManager()
        client = db.get_client()
        if not client:
            logger.warning("Supabase client not available")
            return
        
        # Upsert global stats
        record = {
            'id': 'global_stats',
            'data': json.dumps({
                'last_30_days': calculate_stats(all_results, days=30),
                'last_90_days': calculate_stats(all_results, days=90),
                'all_time': stats_global,
                'by_hipodromo': stats_by_hip,
                'updated_at': datetime.now().isoformat()
            }, ensure_ascii=False)
        }
        
        client.table('rendimiento_stats').upsert(record, on_conflict='id').execute()
        logger.info("Uploaded stats to Supabase (rendimiento_stats)")
        
        # Upload ALL results for detail table
        for r in all_results:
            rec = {
                'fecha': r['fecha'],
                'hipodromo': r['hipodromo'],
                'nro_carrera': r['nro_carrera'],
                'acierto_ganador': r['acierto_ganador'],
                'acierto_quiniela': r['acierto_quiniela'],
                'acierto_trifecta': r['acierto_trifecta'],
                'acierto_superfecta': r['acierto_superfecta'],
                'prediccion_top4': r['prediccion_top4'],
                'resultado_top4': r['resultado_top4']
            }
            try:
                client.table('rendimiento_historico').upsert(
                    rec, on_conflict='fecha,hipodromo,nro_carrera'
                ).execute()
            except Exception as e:
                logger.error(f"Failed to upload record {rec['fecha']} {rec['hipodromo']}: {e}")
        
        logger.info(f"Uploaded {len(all_results)} records to Supabase (rendimiento_historico)")
        
    except Exception as e:
        if 'PGRST205' in str(e) or 'schema cache' in str(e):
            logger.warning(f"Supabase tables not found. Run sql/create_rendimiento_tables.sql in Supabase SQL Editor.")
        else:
            logger.warning(f"Supabase upload skipped: {e}")


def run():
    """Main function."""
    logger.info("=" * 60)
    logger.info("CALCULATING PERFORMANCE METRICS (Supabase + SQLite)")
    logger.info("=" * 60)
    
    # 1. Get predictions from Supabase
    logger.info("\n[1/4] Fetching predictions from Supabase...")
    predictions_by_race = get_predictions_from_supabase()
    
    if not predictions_by_race:
        logger.warning("No predictions found in Supabase. Exiting.")
        return
    
    # 2. Get results from SQLite
    logger.info("\n[2/4] Fetching results from SQLite...")
    results_by_race = get_results_from_sqlite()
    
    if not results_by_race:
        logger.warning("No results found in SQLite. Exiting.")
        return
    
    # 3. Match predictions with results
    logger.info("\n[3/4] Matching predictions with results...")
    results = match_predictions_with_results(predictions_by_race, results_by_race)
    logger.info(f"Found {len(results)} races with both predictions and results")
    
    if not results:
        logger.warning("No matching data found. Exiting.")
        return
    
    # 4. Calculate global stats
    logger.info("\n[4/4] Calculating stats...")
    stats_global = calculate_stats(results)
    logger.info(f"Global: Ganador {stats_global['ganador_pct']}%, Quiniela {stats_global['quiniela_pct']}%, "
                f"Trifecta {stats_global['trifecta_pct']}%, Superfecta {stats_global['superfecta_pct']}%")
    
    # Calculate by hipodromo
    stats_by_hip = calculate_stats_by_hipodromo(results)
    for hip, stats in stats_by_hip.items():
        logger.info(f"  {hip}: {stats['total_carreras']} races, Ganador {stats['ganador_pct']}%")
    
    # Save results
    logger.info("\nSaving results...")
    save_to_sqlite(results)
    save_stats_json(stats_global, stats_by_hip, results)
    upload_to_supabase(stats_global, stats_by_hip, results)
    
    logger.info("\n" + "=" * 60)
    logger.info("PERFORMANCE CALCULATION COMPLETE")
    logger.info("=" * 60)


if __name__ == "__main__":
    run()
