
import sys
import os
import sqlite3
import pandas as pd
import time
import json
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
# We need to import the sync system function to simulate it
sys.path.append(os.path.dirname(__file__))

from src.models.data_manager import obtener_patrones_la_tercera, calcular_todos_patrones
try:
    from sync_system import precalculate_patterns
except ImportError:
    print("Could not import precalculate_patterns from sync_system. Check path or syntax.")
    sys.exit(1)

DB_PATH = 'data/db/hipica_data.db'

def get_db_connection():
    return sqlite3.connect(DB_PATH)

def create_race_result(conn, fecha, carrera_nro, horses_top4):
    """
    Creates a race result with specific top 4 horses.
    """
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO hipodromos (nombre) VALUES ('TEST_HIP')")
    cursor.execute("SELECT id FROM hipodromos WHERE nombre = 'TEST_HIP'")
    hip_id = cursor.fetchone()[0]
    cursor.execute("INSERT INTO jornadas (fecha, hipodromo_id) VALUES (?, ?)", (fecha, hip_id))
    jor_id = cursor.lastrowid
    cursor.execute("INSERT INTO carreras (jornada_id, numero, distancia, tipo, pista) VALUES (?, ?, 1000, 'HANDICAP', 'ARENA')", (jor_id, carrera_nro))
    car_id = cursor.lastrowid
    cursor.execute("INSERT OR IGNORE INTO jinetes (nombre) VALUES ('TEST_JOCKEY')")
    cursor.execute("SELECT id FROM jinetes WHERE nombre = 'TEST_JOCKEY'")
    jinete_id = cursor.fetchone()[0]

    for pos, h_name in enumerate(horses_top4, 1):
        cursor.execute("INSERT OR IGNORE INTO caballos (nombre) VALUES (?)", (h_name,))
        cursor.execute("SELECT id FROM caballos WHERE nombre = ?", (h_name,))
        c_id = cursor.fetchone()[0]
        cursor.execute("""
            INSERT INTO participaciones (carrera_id, caballo_id, jinete_id, posicion, mandil)
            VALUES (?, ?, ?, ?, ?)
        """, (car_id, c_id, jinete_id, pos, pos))
    conn.commit()

def cleanup(conn):
    print("Cleaning up test data...")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM hipodromos WHERE nombre='TEST_HIP'")
    res = cursor.fetchone()
    if not res: return
    hip_id = res[0]
    cursor.execute("SELECT id FROM jornadas WHERE hipodromo_id = ?", (hip_id,))
    j_ids = [r[0] for r in cursor.fetchall()]
    if j_ids:
        j_ids_str = ','.join(map(str, j_ids))
        cursor.execute(f"SELECT id FROM carreras WHERE jornada_id IN ({j_ids_str})")
        c_ids = [r[0] for r in cursor.fetchall()]
        if c_ids:
            c_ids_str = ','.join(map(str, c_ids))
            cursor.execute(f"DELETE FROM participaciones WHERE carrera_id IN ({c_ids_str})")
            cursor.execute(f"DELETE FROM carreras WHERE id IN ({c_ids_str})")
        cursor.execute(f"DELETE FROM jornadas WHERE id IN ({j_ids_str})")
    cursor.execute("DELETE FROM hipodromos WHERE id = ?", (hip_id,))
    conn.commit()

def main():
    print("--- START SYNC PATTERN VERIFICATION ---")
    conn = get_db_connection()
    cleanup(conn)
    
    # Remove existing cache to be clean
    cache_path = Path("data/cache_patrones.json")
    if cache_path.exists():
        cache_path.unlink()
    
    try:
        # 1. Insert 2 Matching Races
        print("1. Inserting Matching Races (Creating Pattern)...")
        create_race_result(conn, '2099-01-01', 1, ['HORSE_A', 'HORSE_B', 'HORSE_C', 'HORSE_D'])
        create_race_result(conn, '2099-01-02', 1, ['HORSE_A', 'HORSE_B', 'HORSE_X', 'HORSE_Y'])
        
        # 2. Verify View uses Live Data (Fallback) if cache is missing
        print("2. Checking View without Cache...")
        pats_live = obtener_patrones_la_tercera(hipodromo_filtro='TEST_HIP')
        print(f"   Patterns count (Live): {len(pats_live)}")
        if len(pats_live) == 0:
             print("FAILURE: Should see pattern via live fallback.")
        
        # 3. RUN SYNC (Calculate & Cache)
        print("3. Running Sync Pre-calculation...")
        success = precalculate_patterns(update_mode=True)
        if not success:
            print("FAILURE: precalculate_patterns returned False")
        
        if not cache_path.exists():
            print("FAILURE: Cache file not created.")
        else:
            print("SUCCESS: Cache file created.")
            
        # 4. Verify View uses Cache
        # We can check this by modifying the cache manually and seeing if view picks it up?
        # Or just trust it.
        # Let's modify the cache content slightly to prove it's being read.
        
        with open(cache_path, 'r') as f:
            data = json.load(f)
            
        # Corrupt/Mark the data
        if data:
            data[0]['tipo'] = "TEST_CACHE_MARKER"
            with open(cache_path, 'w') as f:
                json.dump(data, f)
                
        print("4. Checking View loads from Cache (Modified Marker)...")
        pats_cached = obtener_patrones_la_tercera(hipodromo_filtro='TEST_HIP')
        
        found_marker = any(p['tipo'] == "TEST_CACHE_MARKER" for p in pats_cached)
        
        if found_marker:
            print("✅ SUCCESS: Application is reading from generated JSON cache.")
        else:
            print("❌ FAILURE: Application did NOT read from cache (or filtering logic hides it).")
            # If filtering hides it (because marker changed?), we check raw length
            
    finally:
        cleanup(conn)
        conn.close()
        # Clean cache
        if cache_path.exists():
             cache_path.unlink()
        print("--- END VERIFICATION ---")

if __name__ == '__main__':
    main()
