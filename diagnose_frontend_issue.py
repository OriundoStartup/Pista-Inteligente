"""Comprehensive check to understand why Feb 1 predictions are showing"""
from src.utils.supabase_client import SupabaseManager
from datetime import datetime
import pytz

client = SupabaseManager()
if not client.get_client():
    print("❌ No se pudo conectar a Supabase")
    exit(1)

chile_tz = pytz.timezone('America/Santiago')
today = datetime.now(chile_tz).strftime('%Y-%m-%d')

print("="*70)
print(f"DIAGNÓSTICO COMPLETO - Fecha actual: {today}")
print("="*70)

# Get Valparaíso hipódromo ID
hip_res = client.get_client().table('hipodromos').select('id, nombre').execute()
valpo = [h for h in hip_res.data if 'Valparaíso' in h['nombre']][0]
valpo_id = valpo['id']
print(f"\nHipódromo: {valpo['nombre']} (ID: {valpo_id})")

# Check jornadas for Feb 1 and Feb 16
print("\n1️⃣ JORNADAS:")
for fecha in ['2026-02-01', '2026-02-16']:
    jorn_res = client.get_client().table('jornadas')\
        .select('id, fecha')\
        .eq('hipodromo_id', valpo_id)\
        .eq('fecha', fecha)\
        .execute()
    
    if jorn_res.data:
        jornada = jorn_res.data[0]
        print(f"\n  📅 {fecha}:")
        print(f"     Jornada ID: {jornada['id']}")
        
        # Get carreras
        car_res = client.get_client().table('carreras')\
            .select('id, numero')\
            .eq('jornada_id', jornada['id'])\
            .execute()
        
        carrera_ids = [c['id'] for c in car_res.data]
        print(f"     Total carreras: {len(car_res.data)}")
        
        # Check for results (participaciones)
        if carrera_ids:
            part_res = client.get_client().table('participaciones')\
                .select('carrera_id')\
                .in_('carrera_id', carrera_ids)\
                .execute()
            
            races_with_results = set([p['carrera_id'] for p in part_res.data])
            races_without_results = [c for c in car_res.data if c['id'] not in races_with_results]
            
            print(f"     Carreras CON resultados: {len(races_with_results)}")
            print(f"     Carreras SIN resultados: {len(races_without_results)}")
            
            if races_without_results:
                print(f"     ⚠️ Carreras sin resultados (aparecerán en frontend):")
                for c in races_without_results[:5]:
                    print(f"        - Carrera #{c['numero']} (ID: {c['id']})")
            
            # Check predictions
            pred_res = client.get_client().table('predicciones')\
                .select('carrera_id')\
                .in_('carrera_id', carrera_ids)\
                .execute()
            
            print(f"     Predicciones totales: {len(pred_res.data)}")
            
            # Predictions for races without results
            preds_no_results = [p for p in pred_res.data if p['carrera_id'] in [c['id'] for c in races_without_results]]
            print(f"     Predicciones para carreras SIN resultados: {len(preds_no_results)}")
            
            if fecha == '2026-02-01' and len(preds_no_results) > 0:
                print(f"\n     🚨 PROBLEMA IDENTIFICADO:")
                print(f"        {len(races_without_results)} carreras del {fecha} NO tienen resultados")
                print(f"        Esto hace que aparezcan como 'activas' en el frontend")

# Check what the frontend query would return
print("\n" + "="*70)
print("2️⃣ SIMULACIÓN DE QUERY DEL FRONTEND:")
print("="*70)

# Step 1: Get future jornadas (fecha >= today)
jornadas_res = client.get_client().table('jornadas')\
    .select('id, fecha, hipodromo_id')\
    .eq('hipodromo_id', valpo_id)\
    .gte('fecha', today)\
    .order('fecha')\
    .limit(5)\
    .execute()

print(f"\nJornadas futuras encontradas: {len(jornadas_res.data)}")
for j in jornadas_res.data:
    print(f"  - Fecha: {j['fecha']}, ID: {j['id']}")

if jornadas_res.data:
    # Step 2: Get carreras for those jornadas
    jornada_ids = [j['id'] for j in jornadas_res.data]
    carreras_res = client.get_client().table('carreras')\
        .select('id, numero, jornada_id')\
        .in_('jornada_id', jornada_ids)\
        .execute()
    
    print(f"\nCarreras totales: {len(carreras_res.data)}")
    
    # Step 3: Filter out completed races
    all_race_ids = [c['id'] for c in carreras_res.data]
    results_res = client.get_client().table('participaciones')\
        .select('carrera_id')\
        .in_('carrera_id', all_race_ids)\
        .execute()
    
    completed_set = set([r['carrera_id'] for r in results_res.data])
    active_carreras = [c for c in carreras_res.data if c['id'] not in completed_set]
    
    print(f"Carreras completadas (filtradas): {len(completed_set)}")
    print(f"Carreras activas (se mostrarán): {len(active_carreras)}")
    
    # Group by jornada
    from collections import defaultdict
    by_jornada = defaultdict(list)
    for c in active_carreras:
        jornada = next((j for j in jornadas_res.data if j['id'] == c['jornada_id']), None)
        if jornada:
            by_jornada[jornada['fecha']].append(c['numero'])
    
    print("\n📊 CARRERAS QUE SE MOSTRARÁN EN EL FRONTEND:")
    for fecha, numeros in sorted(by_jornada.items()):
        status = "🚨" if fecha < today else "✅"
        print(f"  {status} {fecha}: {len(numeros)} carreras - {sorted(numeros)[:10]}")

print("\n" + "="*70)
print("✅ DIAGNÓSTICO COMPLETADO")
print("="*70)
