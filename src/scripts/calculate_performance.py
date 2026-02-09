"""
Calculate Performance Metrics: Compares predictions vs actual results.
Calculates: Ganador Exacto, Quiniela, Trifecta, Superfecta

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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_PATH = 'data/db/hipica_data.db'


def get_predictions_with_results():
    """
    Joins predictions with actual race results.
    Returns list of races with predictions and outcomes.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all prediction races that have results
    query = """
    SELECT DISTINCT 
        p.fecha_carrera as fecha,
        p.hipodromo,
        p.nro_carrera
    FROM predicciones p
    INNER JOIN jornadas j ON p.fecha_carrera = j.fecha
    INNER JOIN hipodromos h ON j.hipodromo_id = h.id AND h.nombre = p.hipodromo
    INNER JOIN carreras c ON c.jornada_id = j.id AND c.numero = p.nro_carrera
    INNER JOIN participaciones part ON part.carrera_id = c.id
    WHERE part.posicion IS NOT NULL AND part.posicion > 0
    ORDER BY p.fecha_carrera DESC, p.hipodromo, p.nro_carrera
    """
    
    cursor.execute(query)
    races = cursor.fetchall()
    
    results = []
    
    for race in races:
        fecha = race['fecha']
        hipodromo = race['hipodromo']
        nro_carrera = race['nro_carrera']
        
        # Get predictions for this race (ordered by ranking)
        cursor.execute("""
            SELECT numero_caballo, ranking_prediccion, caballo_id,
                   json_extract(metadata, '$.caballo') as caballo_nombre
            FROM predicciones
            WHERE fecha_carrera = ? AND hipodromo = ? AND nro_carrera = ?
            ORDER BY ranking_prediccion ASC
            LIMIT 4
        """, (fecha, hipodromo, nro_carrera))
        
        preds = cursor.fetchall()
        if not preds:
            continue
            
        # Get actual results for this race
        cursor.execute("""
            SELECT part.posicion, part.caballo_id, cab.nombre as caballo_nombre
            FROM participaciones part
            INNER JOIN carreras c ON part.carrera_id = c.id
            INNER JOIN jornadas j ON c.jornada_id = j.id
            INNER JOIN hipodromos h ON j.hipodromo_id = h.id
            INNER JOIN caballos cab ON part.caballo_id = cab.id
            WHERE j.fecha = ? AND h.nombre = ? AND c.numero = ?
            AND part.posicion IS NOT NULL AND part.posicion > 0
            ORDER BY part.posicion ASC
            LIMIT 4
        """, (fecha, hipodromo, nro_carrera))
        
        actual = cursor.fetchall()
        if not actual:
            continue
        
        # Build result object
        pred_caballos = [p['caballo_id'] for p in preds]
        actual_caballos = [a['caballo_id'] for a in actual]
        
        # Calculate hits
        ganador_exacto = len(pred_caballos) > 0 and len(actual_caballos) > 0 and pred_caballos[0] == actual_caballos[0]
        
        # Quiniela: Top 2 preds contain actual 1st and 2nd (any order)
        quiniela = False
        if len(pred_caballos) >= 2 and len(actual_caballos) >= 2:
            pred_top2 = set(pred_caballos[:2])
            actual_top2 = set(actual_caballos[:2])
            quiniela = pred_top2 == actual_top2
        
        # Trifecta: Top 3 preds contain actual 1st, 2nd, 3rd (any order)
        trifecta = False
        if len(pred_caballos) >= 3 and len(actual_caballos) >= 3:
            pred_top3 = set(pred_caballos[:3])
            actual_top3 = set(actual_caballos[:3])
            trifecta = pred_top3 == actual_top3
        
        # Superfecta: Top 4 preds contain actual 1st, 2nd, 3rd, 4th (any order)
        superfecta = False
        if len(pred_caballos) >= 4 and len(actual_caballos) >= 4:
            pred_top4 = set(pred_caballos[:4])
            actual_top4 = set(actual_caballos[:4])
            superfecta = pred_top4 == actual_top4
        
        results.append({
            'fecha': fecha,
            'hipodromo': hipodromo,
            'nro_carrera': nro_carrera,
            'acierto_ganador': ganador_exacto,
            'acierto_quiniela': quiniela,
            'acierto_trifecta': trifecta,
            'acierto_superfecta': superfecta,
            'prediccion_top4': [p['caballo_nombre'] or f"ID:{p['caballo_id']}" for p in preds[:4]],
            'resultado_top4': [a['caballo_nombre'] for a in actual[:4]]
        })
    
    conn.close()
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
    """Group results by hipódromo and calculate stats for each."""
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
    logger.info(f"✅ Saved {len(results)} records to rendimiento_historico")


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
        'recent_races': recent_results[:50]  # Last 50 races for detail table
    }
    
    os.makedirs('data', exist_ok=True)
    with open('data/rendimiento_stats.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    logger.info("✅ Saved stats to data/rendimiento_stats.json")


def upload_to_supabase(stats_global, stats_by_hip, recent_results):
    """Upload stats to Supabase for frontend."""
    try:
        from src.utils.supabase_client import SupabaseManager
        
        db = SupabaseManager()
        client = db.get_client()
        if not client:
            logger.warning("⚠️ Supabase client not available")
            return
        
        # Upsert global stats
        record = {
            'id': 'global_stats',
            'data': json.dumps({
                'last_30_days': calculate_stats(recent_results, days=30),
                'last_90_days': calculate_stats(recent_results, days=90),
                'all_time': stats_global,
                'by_hipodromo': stats_by_hip,
                'updated_at': datetime.now().isoformat()
            }, ensure_ascii=False)
        }
        
        client.table('rendimiento_stats').upsert(record, on_conflict='id').execute()
        logger.info("✅ Uploaded stats to Supabase (rendimiento_stats)")
        
        # Upload recent results for detail table
        # Uploading all results to ensure history is complete in Supabase
        for r in recent_results:
            rec = {
                'fecha': r['fecha'],
                'hipodromo': r['hipodromo'],
                'nro_carrera': r['nro_carrera'],
                'acierto_ganador': r['acierto_ganador'],
                'acierto_quiniela': r['acierto_quiniela'],
                'acierto_trifecta': r['acierto_trifecta'],
                'acierto_superfecta': r['acierto_superfecta'],
                'prediccion_top4': r['prediccion_top4'],  # Pass list directly, client handles JSON
                'resultado_top4': r['resultado_top4']
            }
            try:
                client.table('rendimiento_historico').upsert(
                    rec, on_conflict='fecha,hipodromo,nro_carrera'
                ).execute()
            except Exception as e:
                logger.error(f"Failed to upload record {rec['fecha']} {rec['hipodromo']}: {e}")
        
        logger.info(f"✅ Uploaded {len(recent_results)} records to Supabase (rendimiento_historico)")
        
    except Exception as e:
        if 'PGRST205' in str(e) or 'schema cache' in str(e):
            logger.warning(f"⚠️ Supabase tables not found. Run sql/create_rendimiento_tables.sql in Supabase SQL Editor.")
        else:
            logger.warning(f"⚠️ Supabase upload skipped: {e}")


def run():
    """Main function."""
    logger.info("=" * 60)
    logger.info("CALCULATING PERFORMANCE METRICS")
    logger.info("=" * 60)
    
    # 1. Get all predictions with results
    logger.info("\n[1/4] Matching predictions with results...")
    results = get_predictions_with_results()
    logger.info(f"Found {len(results)} races with both predictions and results")
    
    if not results:
        logger.warning("No matching data found. Exiting.")
        return
    
    # 2. Calculate global stats
    logger.info("\n[2/4] Calculating global stats...")
    stats_global = calculate_stats(results)
    logger.info(f"Global: Ganador {stats_global['ganador_pct']}%, Quiniela {stats_global['quiniela_pct']}%, "
                f"Trifecta {stats_global['trifecta_pct']}%, Superfecta {stats_global['superfecta_pct']}%")
    
    # 3. Calculate by hipódromo
    logger.info("\n[3/4] Calculating stats by hipódromo...")
    stats_by_hip = calculate_stats_by_hipodromo(results)
    for hip, stats in stats_by_hip.items():
        logger.info(f"  {hip}: {stats['total_carreras']} races, Ganador {stats['ganador_pct']}%")
    
    # 4. Save results
    logger.info("\n[4/4] Saving results...")
    save_to_sqlite(results)
    save_stats_json(stats_global, stats_by_hip, results)
    upload_to_supabase(stats_global, stats_by_hip, results)
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ PERFORMANCE CALCULATION COMPLETE")
    logger.info("=" * 60)


if __name__ == "__main__":
    run()
