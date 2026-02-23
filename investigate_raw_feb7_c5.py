import os
import sys
sys.path.append(os.path.abspath('.'))

from src.utils.supabase_client import SupabaseManager

db = SupabaseManager()
client = db.get_client()

print("=" * 70)
print("DATOS RAW: FEB 7 CARRERA 5")
print("=" * 70)

# Get raw predictions from predicciones table
print("\n🤖 PREDICCIONES (desde tabla predicciones):")
preds_result = client.table('predicciones').select(
    '*,carreras!inner(numero,jornadas!inner(fecha,hipodromos!inner(nombre)))'
).execute()

feb7_c5_preds = []
for p in (preds_result.data or []):
    fecha = p.get('carreras', {}).get('jornadas', {}).get('fecha')
    nro = p.get('carreras', {}).get('numero')
    if fecha == '2026-02-07' and nro == 5:
        feb7_c5_preds.append(p)

if feb7_c5_preds:
    # Sort by rank
    feb7_c5_preds.sort(key=lambda x: x.get('rank_predicho', 999))
    print(f"  Total predicciones: {len(feb7_c5_preds)}")
    print(f"\n  TOP 4 PREDICHOS:")
    for i, p in enumerate(feb7_c5_preds[:4], 1):
        print(f"    {i}. {p.get('caballo')} (#{p.get('numero_caballo')}) - Prob: {p.get('probabilidad', 0):.3f}")
else:
    print("  ❌ NO HAY PREDICCIONES")

# Get results from resultados (if exists) or participaciones
print("\n🏁 RESULTADOS REALES:")
import sqlite3
try:
    conn = sqlite3.connect('data/hipica.db')
    cursor = conn.cursor()
    
    # Find Feb 7 jornada
    cursor.execute("""
        SELECT j.id FROM jornadas j
        JOIN hipodromos h ON j.hipodromo_id = h.id
        WHERE j.fecha = '2026-02-07' AND h.nombre = 'Hipódromo Chile'
    """)
    jornada_row = cursor.fetchone()
    
    if jornada_row:
        jornada_id = jornada_row[0]
        
        # Get carrera 5
        cursor.execute("""
            SELECT id FROM carreras
            WHERE jornada_id = ? AND numero = 5
        """, (jornada_id,))
        carrera_row = cursor.fetchone()
        
        if carrera_row:
            carrera_id = carrera_row[0]
            
            # Get top 4 finishers
            cursor.execute("""
                SELECT p.posicion, c.nombre, p.numero
                FROM participaciones p
                JOIN caballos c ON p.caballo_id = c.id
                WHERE p.carrera_id = ? AND p.posicion IS NOT NULL AND p.posicion <= 4
                ORDER BY p.posicion
            """, (carrera_id,))
            
            resultados = cursor.fetchall()
            if resultados:
                print(f"  Total caballos con posición: {len(resultados)}")
                print(f"\n  TOP 4 REALES:")
                for pos, nombre, numero in resultados:
                    print(f"    {pos}. {nombre} (#{numero})")
            else:
                print("  ❌ NO HAY RESULTADOS CON POSICIONES")
        else:
            print("  ❌ NO EXISTE CARRERA 5")
    else:
        print("  ❌ NO EXISTE JORNADA FEB 7")
    
    conn.close()
except Exception as e:
    print(f"  ❌ Error: {e}")

# Now compare
if feb7_c5_preds and 'resultados' in locals() and resultados:
    print("\n" + "=" * 70)
    print("COMPARACIÓN")
    print("=" * 70)
    
    pred_top4 = [p.get('caballo') for p in feb7_c5_preds[:4]]
    real_top4 = [nombre for _, nombre, _ in resultados]
    
    print(f"\nPredicción: {pred_top4}")
    print(f"Real:       {real_top4}")
    
    # Check matches
    ganador = pred_top4[0] == real_top4[0] if len(pred_top4) > 0 and len(real_top4) > 0 else False
    quiniela = set(pred_top4[:2]) == set(real_top4[:2]) if len(pred_top4) >= 2 and len(real_top4) >= 2 else False
    trifecta = pred_top4[:3] == real_top4[:3] if len(pred_top4) >= 3 and len(real_top4) >= 3 else False
    superfecta = pred_top4 == real_top4 if len(pred_top4) == 4 and len(real_top4) == 4 else False
    
    print(f"\n🎯 ACIERTOS:")
    print(f"  Ganador: {'✅' if ganador else '❌'}")
    print(f"  Quiniela: {'✅' if quiniela else '❌'}")
    print(f"  Trifecta: {'✅✅✅' if trifecta else '❌'}")
    print(f"  Superfecta: {'✅' if superfecta else '❌'}")
