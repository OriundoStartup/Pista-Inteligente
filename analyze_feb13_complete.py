"""Comprehensive analysis of Feb 13 predictions vs results"""
import sqlite3
from src.utils.supabase_client import SupabaseManager
import json

fecha = '2026-02-13'

print("="*80)
print(f"ANALISIS COMPLETO: PREDICCIONES VS RESULTADOS - {fecha}")
print("="*80)

# Connect to SQLite
conn = sqlite3.connect('data/db/hipica_data.db')
cursor = conn.cursor()

# Get Supabase client
client = SupabaseManager().get_client()

# Get all jornadas for Feb 13
jornadas = cursor.execute("""
    SELECT j.id, j.fecha, h.id as hip_id, h.nombre as hipodromo
    FROM jornadas j
    JOIN hipodromos h ON j.hipodromo_id = h.id
    WHERE j.fecha = ?
    ORDER BY h.nombre
""", (fecha,)).fetchall()

print(f"\nJornadas encontradas: {len(jornadas)}")

total_carreras = 0
carreras_con_predicciones = 0
carreras_con_resultados = 0
carreras_con_ambos = 0

matches_ganador = 0
matches_quiniela = 0  
matches_trifecta = 0
matches_superfecta = 0

discrepancias = []

for jornada_id, fecha_j, hip_id, hipodromo in jornadas:
    print(f"\n{'='*80}")
    print(f"HIPODROMO: {hipodromo}")
    print(f"{'='*80}")
    
    # Get carreras for this jornada
    carreras = cursor.execute("""
        SELECT id, numero
        FROM carreras
        WHERE jornada_id = ?
        ORDER BY numero
    """, (jornada_id,)).fetchall()
    
    print(f"Total carreras: {len(carreras)}")
    total_carreras += len(carreras)
    
    for carrera_id, nro_carrera in carreras:
        # Get results from SQLite
        results = cursor.execute("""
            SELECT p.posicion, p.numero_mandil, c.nombre as caballo
            FROM participaciones p
            JOIN caballos c ON p.caballo_id = c.id
            WHERE p.carrera_id = ? AND p.posicion IS NOT NULL AND p.posicion > 0
            ORDER BY p.posicion
            LIMIT 4
        """, (carrera_id,)).fetchall()
        
        has_results = len(results) > 0
        if has_results:
            carreras_con_resultados += 1
        
        # Get predictions from Supabase
        try:
            pred_res = client.table('predicciones') \
                .select('numero_caballo, caballo, rank_predicho') \
                .eq('carrera_id', carrera_id) \
                .order('rank_predicho') \
                .limit(4) \
                .execute()
            
            has_predictions = len(pred_res.data) > 0
            if has_predictions:
                carreras_con_predicciones += 1
        except:
            has_predictions = False
            pred_res = None
        
        # Only analyze if we have both
        if not has_results or not has_predictions:
            continue
        
        carreras_con_ambos += 1
        
        # Normalize names
        pred_names = [p['caballo'].upper().strip() for p in pred_res.data]
        result_names = [r[2].upper().strip() for r in results]
        
        # Calculate matches
        ganador = (pred_names[0] == result_names[0]) if len(pred_names) > 0 and len(result_names) > 0 else False
        quiniela = (pred_names[:2] == result_names[:2]) if len(pred_names) >= 2 and len(result_names) >= 2 else False
        trifecta = (pred_names[:3] == result_names[:3]) if len(pred_names) >= 3 and len(result_names) >= 3 else False
        superfecta = (pred_names[:4] == result_names[:4]) if len(pred_names) >= 4 and len(result_names) >= 4 else False
        
        if ganador:
            matches_ganador += 1
        if quiniela:
            matches_quiniela += 1
        if trifecta:
            matches_trifecta += 1
        if superfecta:
            matches_superfecta += 1
        
        # Check what's stored in rendimiento_historico
        stored = cursor.execute("""
            SELECT acierto_ganador, acierto_quiniela, acierto_trifecta, acierto_superfecta
            FROM rendimiento_historico
            WHERE fecha = ? AND hipodromo = ? AND nro_carrera = ?
        """, (fecha, hipodromo, nro_carrera)).fetchone()
        
        # Find discrepancies
        if stored:
            stored_ganador, stored_quiniela, stored_trifecta, stored_superfecta = stored
            
            if bool(stored_superfecta) != superfecta:
                discrepancias.append({
                    'hipodromo': hipodromo,
                    'carrera': nro_carrera,
                    'tipo': 'SUPERFECTA',
                    'calculado': superfecta,
                    'almacenado': bool(stored_superfecta),
                    'prediccion': pred_names[:4],
                    'resultado': result_names[:4]
                })
            
            if bool(stored_trifecta) != trifecta:
                discrepancias.append({
                    'hipodromo': hipodromo,
                    'carrera': nro_carrera,
                    'tipo': 'TRIFECTA',
                    'calculado': trifecta,
                    'almacenado': bool(stored_trifecta),
                    'prediccion': pred_names[:3],
                    'resultado': result_names[:3]
                })

# Print summary
print(f"\n{'='*80}")
print("RESUMEN")
print(f"{'='*80}")
print(f"Total carreras: {total_carreras}")
print(f"Carreras con resultados: {carreras_con_resultados}")
print(f"Carreras con predicciones: {carreras_con_predicciones}")
print(f"Carreras con AMBOS: {carreras_con_ambos}")

print(f"\nMATCHES ENCONTRADOS:")
print(f"  Ganador exacto: {matches_ganador} de {carreras_con_ambos} ({matches_ganador/carreras_con_ambos*100:.1f}%)")
print(f"  Quiniela: {matches_quiniela} de {carreras_con_ambos} ({matches_quiniela/carreras_con_ambos*100:.1f}%)")
print(f"  Trifecta: {matches_trifecta} de {carreras_con_ambos} ({matches_trifecta/carreras_con_ambos*100:.1f}%)")
print(f"  Superfecta: {matches_superfecta} de {carreras_con_ambos} ({matches_superfecta/carreras_con_ambos*100:.1f}%)")

if discrepancias:
    print(f"\n{'='*80}")
    print(f"DISCREPANCIAS ENCONTRADAS: {len(discrepancias)}")
    print(f"{'='*80}")
    
    for disc in discrepancias:
        print(f"\n{disc['hipodromo']} - Carrera #{disc['carrera']} - {disc['tipo']}")
        print(f"  Calculado manualmente: {disc['calculado']}")
        print(f"  Almacenado en BD: {disc['almacenado']}")
        print(f"  Prediccion: {disc['prediccion']}")
        print(f"  Resultado:  {disc['resultado']}")
else:
    print(f"\nNo se encontraron discrepancias")

conn.close()

print(f"\n{'='*80}")
print("ANALISIS COMPLETADO")
print(f"{'='*80}")
