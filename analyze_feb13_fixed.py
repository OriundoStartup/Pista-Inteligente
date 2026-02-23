"""Analyze Feb 13 predictions vs results - FIXED"""
import sqlite3
from src.utils.supabase_client import SupabaseManager

conn = sqlite3.connect('data/db/hipica_data.db')
cursor = conn.cursor()
client = SupabaseManager().get_client()

fecha = '2026-02-13'
hipodromo = 'Club Hipico de Santiago'

print("="*70)
print(f"ANALISIS: {hipodromo} - {fecha}")
print("="*70)

# Get jornada
jornada = cursor.execute("""
    SELECT j.id
    FROM jornadas j
    JOIN hipodromos h ON j.hipodromo_id = h.id
    WHERE j.fecha = ? AND h.nombre LIKE ?
""", (fecha, '%Santiago%')).fetchone()

if not jornada:
    print("No se encontro jornada")
    conn.close()
    exit()

jornada_id = jornada[0]

# Get carreras
carreras = cursor.execute("""
    SELECT id, numero FROM carreras WHERE jornada_id = ? ORDER BY numero
""", (jornada_id,)).fetchall()

print(f"\nTotal carreras: {len(carreras)}")

stats = {'ganador': 0, 'quiniela': 0, 'trifecta': 0, 'superfecta': 0, 'total': 0}
false_positives = []

for carrera_id, nro in carreras:
    # Get results
    results = cursor.execute("""
        SELECT c.nombre
        FROM participaciones p
        JOIN caballos c ON p.caballo_id = c.id
        WHERE p.carrera_id = ? AND p.posicion > 0
        ORDER BY p.posicion LIMIT 4
    """, (carrera_id,)).fetchall()
    
    if not results or len(results) < 4:
        continue
    
    # Get predictions from Supabase
    try:
        preds = client.table('predicciones')\
            .select('caballo')\
            .eq('carrera_id', carrera_id)\
            .order('rank_predicho')\
            .limit(4)\
            .execute()
        
        if not preds.data or len(preds.data) < 4:
            continue
    except Exception as e:
        print(f"Error carrera {nro}: {e}")
        continue
    
    stats['total'] += 1
    
    # Normalize names
    pred_names = [p['caballo'].upper().strip() for p in preds.data]
    real_names = [r[0].upper().strip() for r in results]
    
    # Calculate matches
    ganador = pred_names[0] == real_names[0]
    quiniela = pred_names[:2] == real_names[:2]
    trifecta = pred_names[:3] == real_names[:3]
    superfecta = pred_names[:4] == real_names[:4]
    
    if ganador:
        stats['ganador'] += 1
    if quiniela:
        stats['quiniela'] += 1
    if trifecta:
        stats['trifecta'] += 1
    if superfecta:
        stats['superfecta'] += 1
        print(f"\nCarrera {nro}: SUPERFECTA!")
        print(f"  Prediccion: {pred_names}")
        print(f"  Resultado:  {real_names}")
    
    # Check stored match
    stored = cursor.execute("""
        SELECT acierto_superfecta FROM rendimiento_historico
        WHERE fecha = ? AND nro_carrera = ?
    """, (fecha, nro)).fetchone()
    
    if stored and bool(stored[0]) and not superfecta:
        false_positives.append({
            'carrera': nro,
            'stored': True,
            'actual': False,
            'pred': pred_names,
            'real': real_names
        })

conn.close()

print(f"\n{'='*70}")
print("RESULTADOS:")
print(f"  Carreras analizadas: {stats['total']}")
if stats['total'] > 0:
    print(f"  Ganador:   {stats['ganador']} ({stats['ganador']/stats['total']*100:.1f}%)")
    print(f"  Quiniela:  {stats['quiniela']} ({stats['quiniela']/stats['total']*100:.1f}%)")
    print(f"  Trifecta:  {stats['trifecta']} ({stats['trifecta']/stats['total']*100:.1f}%)")
    print(f"  Superfecta: {stats['superfecta']} ({stats['superfecta']/stats['total']*100:.1f}%)")

if false_positives:
    print(f"\nFALSOS POSITIVOS ENCONTRADOS: {len(false_positives)}")
    for fp in false_positives:
        print(f"\n  Carrera {fp['carrera']}:")
        print(f"    BD dice: Superfecta = True")
        print(f"    Real:    Superfecta = False")
        print(f"    Pred: {fp['pred']}")
        print(f"    Real: {fp['real']}")
else:
    print("\nNo se encontraron falsos positivos")

print("="*70)
