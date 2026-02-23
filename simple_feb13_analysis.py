"""Simplified analysis - Feb 13 predictions vs results"""
import sqlite3
from src.utils.supabase_client import SupabaseManager

fecha = '2026-02-13'

conn = sqlite3.connect('data/db/hipica_data.db')
cursor = conn.cursor()
client = SupabaseManager().get_client()

print("="*70)
print(f"ANALISIS: {fecha}")
print("="*70)

# Get jornadas
jornadas = cursor.execute("""
    SELECT j.id, h.nombre
    FROM jornadas j
    JOIN hipodromos h ON j.hipodromo_id = h.id
    WHERE j.fecha = ?
""", (fecha,)).fetchall()

print(f"\nJornadas: {len(jornadas)}")

total_matches = {
    'ganador': 0,
    'quiniela': 0,
    'trifecta': 0,
    'superfecta': 0
}

total_races = 0

for jornada_id, hipodromo in jornadas:
    print(f"\n{hipodromo}:")
    
    carreras = cursor.execute("""
        SELECT id, numero FROM carreras WHERE jornada_id = ?
    """, (jornada_id,)).fetchall()
    
    for carrera_id, nro in carreras:
        # Get results
        results = cursor.execute("""
            SELECT c.nombre
            FROM participaciones p
            JOIN caballos c ON p.caballo_id = c.id
            WHERE p.carrera_id = ? AND p.posicion > 0
            ORDER BY p.posicion LIMIT 4
        """, (carrera_id,)).fetchall()
        
        if not results:
            continue
        
        # Get predictions
        try:
            preds = client.table('predicciones').select('caballo').eq('carrera_id', carrera_id).order('rank_predicho').limit(4).execute()
            if not preds.data:
                continue
        except:
            continue
        
        total_races += 1
        
        # Normalize
        pred_n = [p['caballo'].upper().strip() for p in preds.data]
        result_n = [r[0].upper().strip() for r in results]
        
        # Check matches
        g = pred_n[0] == result_n[0] if len(pred_n) > 0 and len(result_n) > 0 else False
        q = pred_n[:2] == result_n[:2] if len(pred_n) >= 2 and len(result_n) >= 2 else False
        t = pred_n[:3] == result_n[:3] if len(pred_n) >= 3 and len(result_n) >= 3 else False
        s = pred_n[:4] == result_n[:4] if len(pred_n) >= 4 and len(result_n) >= 4 else False
        
        if g:
            total_matches['ganador'] += 1
        if q:
            total_matches['quiniela'] += 1
        if t:
            total_matches['trifecta'] += 1
        if s:
            total_matches['superfecta'] += 1
            print(f"  Carrera {nro}: SUPERFECTA!")
            print(f"    Pred: {pred_n}")
            print(f"    Real: {result_n}")

conn.close()

print(f"\n{'='*70}")
print("RESUMEN:")
print(f"  Total carreras analizadas: {total_races}")
print(f"  Ganador: {total_matches['ganador']} ({total_matches['ganador']/total_races*100:.1f}%)")
print(f"  Quiniela: {total_matches['quiniela']} ({total_matches['quiniela']/total_races*100:.1f}%)")
print(f"  Trifecta: {total_matches['trifecta']} ({total_matches['trifecta']/total_races*100:.1f}%)")
print(f"  Superfecta: {total_matches['superfecta']} ({total_matches['superfecta']/total_races*100:.1f}%)")
print("="*70)
