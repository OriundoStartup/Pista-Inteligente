"""Verify Carrera 7 specifically - Feb 13"""
import sqlite3
from src.utils.supabase_client import SupabaseManager
import json

conn = sqlite3.connect('data/db/hipica_data.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

fecha = '2026-02-13'
nro_carrera = 7

print("="*70)
print(f"VERIFICACION DETALLADA: Carrera #{nro_carrera} - {fecha}")
print("="*70)

# Get stored match
stored = cursor.execute("""
    SELECT * FROM rendimiento_historico
    WHERE fecha = ? AND nro_carrera = ?
""", (fecha, nro_carrera)).fetchone()

if stored:
    print("\nDATO ALMACENADO EN BD:")
    print(f"  Ganador: {bool(stored['acierto_ganador'])}")
    print(f"  Quiniela: {bool(stored['acierto_quiniela'])}")
    print(f"  Trifecta: {bool(stored['acierto_trifecta'])}")
    print(f"  Superfecta: {bool(stored['acierto_superfecta'])}")
    
    pred_stored = json.loads(stored['prediccion_top4'])
    result_stored = json.loads(stored['resultado_top4'])
    
    print(f"\n  Prediccion guardada: {pred_stored}")
    print(f"  Resultado guardado:  {result_stored}")

# Get actual data from participaciones
jornada = cursor.execute("""
    SELECT j.id FROM jornadas j
    JOIN hipodromos h ON j.hipodromo_id = h.id
    WHERE j.fecha = ? AND h.nombre LIKE '%Santiago%'
""", (fecha,)).fetchone()

if jornada:
    carrera = cursor.execute("""
        SELECT id FROM carreras WHERE jornada_id = ? AND numero = ?
    """, (jornada['id'], nro_carrera)).fetchone()
    
    if carrera:
        results = cursor.execute("""
            SELECT p.posicion, c.nombre
            FROM participaciones p
            JOIN caballos c ON p.caballo_id = c.id
            WHERE p.carrera_id = ? AND p.posicion > 0
            ORDER BY p.posicion LIMIT 4
        """, (carrera['id'],)).fetchall()
        
        print("\nRESULTADOS REALES (desde participaciones):")
        real_names = []
        for r in results:
            real_names.append(r['nombre'].strip())
            print(f"  {r['posicion']}. {r['nombre']}")
        
        # Get predictions from Supabase
        client = SupabaseManager().get_client()
        try:
            preds = client.table('predicciones')\
                .select('caballo, rank_predicho')\
                .eq('carrera_id', carrera['id'])\
                .order('rank_predicho')\
                .limit(4)\
                .execute()
            
            if preds.data:
                print("\nPREDICCIONES (desde Supabase):")
                pred_names = []
                for p in preds.data:
                    pred_names.append(p['caballo'].strip())
                    print(f"  Rank {p['rank_predicho']}: {p['caballo']}")
                
                # Manual comparison
                print("\nCOMPARACION MANUAL:")
                pred_norm = [p.upper().strip() for p in pred_names]
                real_norm = [r.upper().strip() for r in real_names]
                
                print(f"  Pred (norm): {pred_norm}")
                print(f"  Real (norm): {real_norm}")
                
                superfecta_real = pred_norm[:4] == real_norm[:4]
                print(f"\n  Superfecta real: {superfecta_real}")
                print(f"  Superfecta BD:   {bool(stored['acierto_superfecta'])}")
                
                if superfecta_real != bool(stored['acierto_superfecta']):
                    print("\n  ⚠️ DISCREPANCIA DETECTADA!")
        except Exception as e:
            print(f"\nError obteniendo predicciones: {e}")

conn.close()
print("="*70)
