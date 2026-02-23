"""
Test what get_predictions/results functions actually return.
"""
import sqlite3
import os
import sys
from collections import defaultdict

sys.path.append(os.path.abspath('.'))
from src.utils.supabase_client import SupabaseManager

DB_PATH = 'data/db/hipica_data.db'

# Copy of get_predictions_from_supabase
def test_get_predictions():
    db = SupabaseManager()
    client = db.get_client()
    
    result = client.table('predicciones').select(
        '*,'
        'carreras!inner(numero, jornadas!inner(fecha, hipodromos!inner(nombre)))'
    ).execute()
    
    preds = result.data if result.data else []
    
    by_race = defaultdict(list)
    for p in preds:
        carrera =p.get('carreras', {})
        jornada = carrera.get('jornadas', {})
        hipodromo = jornada.get('hipodromos', {})
        
        fecha = jornada.get('fecha')
        hip_nombre = hipodromo.get('nombre')
        nro_carrera = carrera.get('numero')
        
        if not fecha or not hip_nombre or not nro_carrera:
            continue
        
        key = (fecha, hip_nombre, nro_carrera)
        by_race[key].append({'caballo': p.get('caballo')})
    
    return by_race

# Copy of get_results_from_sqlite
def test_get_results():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
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
    
    by_race = defaultdict(list)
    for row in rows:
        key = (row['fecha'], row['hipodromo'], row['nro_carrera'])
        by_race[key].append({
            'posicion': row['posicion'],
            'caballo_nombre': row['caballo_nombre']
        })
    
    return by_race

print("Testing get_predictions_from_supabase()...")
preds = test_get_predictions()
print(f"Total races: {len(preds)}")

feb7_preds = {k: v for k, v in preds.items() if k[0] == '2026-02-07'}
print(f"Feb 7 races: {len(feb7_preds)}")
if feb7_preds:
    sample_key = list(feb7_preds.keys())[0]
    print(f"Sample key: {sample_key}")
    print(f"Key types: ({type(sample_key[0])}, {type(sample_key[1])}, {type(sample_key[2])})")

print("\nTesting get_results_from_sqlite()...")
results = test_get_results()
print(f"Total races: {len(results)}")

feb7_results = {k: v for k, v in results.items() if k[0] == '2026-02-07'}
print(f"Feb 7 races: {len(feb7_results)}")
if feb7_results:
    sample_key = list(feb7_results.keys())[0]
    print(f"Sample key: {sample_key}")
    print(f"Key types: ({type(sample_key[0])}, {type(sample_key[1])}, {type(sample_key[2])})")

print("\nChecking for overlap...")
pred_keys = set(feb7_preds.keys())
result_keys = set(feb7_results.keys())
overlap = pred_keys & result_keys
print(f"Overlapping keys: {len(overlap)}")

if not overlap:
    print("\n❌ NO OVERLAP - MATCHING WILL FAIL")
    if pred_keys and result_keys:
        pk = list(pred_keys)[0]
        rk = list(result_keys)[0]
        print(f"\nPred key example: {pk}")
        print(f"Result key example: {rk}")
        print(f"\nAre they equal? {pk == rk}")
        if pk[0] == rk[0] and pk[2] == rk[2]:
            print(f"Hipódromo mismatch: '{pk[1]}' != '{rk[1]}'")
