"""Check predictions and their associated race dates"""
from src.utils.supabase_client import SupabaseManager

client = SupabaseManager()
if not client.get_client():
    print("❌ No se pudo conectar a Supabase")
    exit(1)

print("="*70)
print("VERIFICACIÓN DE PREDICCIONES Y FECHAS - VALPARAÍSO")
print("="*70)

# Get today's date in Chile timezone
from datetime import datetime
import pytz
chile_tz = pytz.timezone('America/Santiago')
today = datetime.now(chile_tz).strftime('%Y-%m-%d')
print(f"\nFecha de hoy (Chile): {today}")

# Get future jornadas for Valparaíso
print("\n1️⃣ JORNADAS FUTURAS DE VALPARAÍSO:")
jornadas_res = client.get_client().table('jornadas')\
    .select('id, fecha, hipodromos(nombre)')\
    .gte('fecha', today)\
    .execute()

valpo_jornadas = [j for j in jornadas_res.data if j.get('hipodromos') and 'Valparaíso' in j['hipodromos']['nombre']]
print(f"Total jornadas futuras: {len(valpo_jornadas)}")
for j in valpo_jornadas:
    print(f"  - Jornada ID: {j['id']}, Fecha: {j['fecha']}")

if not valpo_jornadas:
    print("⚠️ NO HAY JORNADAS FUTURAS DE VALPARAÍSO")
else:
    # Get carreras for these jornadas
    jornada_ids = [j['id'] for j in valpo_jornadas]
    print(f"\n2️⃣ CARRERAS PARA JORNADAS FUTURAS:")
    carreras_res = client.get_client().table('carreras')\
        .select('id, numero, jornada_id, hora')\
        .in_('jornada_id', jornada_ids)\
        .execute()
    
    print(f"Total carreras: {len(carreras_res.data)}")
    
    # Check which races have results
    carrera_ids = [c['id'] for c in carreras_res.data]
    if carrera_ids:
        results_res = client.get_client().table('participaciones')\
            .select('carrera_id')\
            .in_('carrera_id', carrera_ids)\
            .execute()
        
        completed_races = set([r['carrera_id'] for r in results_res.data])
        print(f"Carreras con resultados (deberían estar ocultas): {len(completed_races)}")
        
        # Active races (without results)
        active_races = [c for c in carreras_res.data if c['id'] not in completed_races]
        print(f"Carreras activas (sin resultados): {len(active_races)}")
        
        # Group by jornada
        from collections import defaultdict
        by_jornada = defaultdict(list)
        for c in active_races:
            jornada = next((j for j in valpo_jornadas if j['id'] == c['jornada_id']), None)
            fecha = jornada['fecha'] if jornada else 'Unknown'
            by_jornada[fecha].append(c['numero'])
        
        print("\nCarreras activas por fecha:")
        for fecha, numeros in sorted(by_jornada.items()):
            print(f"  {fecha}: Carreras {sorted(numeros)}")
        
        # Get predictions for active races
        active_race_ids = [c['id'] for c in active_races]
        if active_race_ids:
            print(f"\n3️⃣ PREDICCIONES PARA CARRERAS ACTIVAS:")
            pred_res = client.get_client().table('predicciones')\
                .select('carrera_id, caballo, numero_caballo')\
                .in_('carrera_id', active_race_ids)\
                .execute()
            
            print(f"Total predicciones: {len(pred_res.data)}")
            
            # Group predictions by race
            preds_by_race = defaultdict(int)
            for p in pred_res.data:
                preds_by_race[p['carrera_id']] += 1
            
            # Map back to dates
            pred_by_fecha = defaultdict(int)
            for race_id, count in preds_by_race.items():
                carrera = next((c for c in active_races if c['id'] == race_id), None)
                if carrera:
                    jornada = next((j for j in valpo_jornadas if j['id'] == carrera['jornada_id']), None)
                    if jornada:
                        pred_by_fecha[jornada['fecha']] += 1
            
            print("\nNúmero de carreras con predicciones por fecha:")
            for fecha, count in sorted(pred_by_fecha.items()):
                print(f"  {fecha}: {count} carreras")

# Check for any Feb 1 data that might be lingering
print("\n" + "="*70)
print("4️⃣ VERIFICACIÓN ESPECÍFICA: DATOS DEL 1 DE FEBRERO")
print("="*70)

feb1_jornada = client.get_client().table('jornadas')\
    .select('id, fecha, hipodromos(nombre)')\
    .eq('fecha', '2026-02-01')\
    .execute()

valpo_feb1 = [j for j in feb1_jornada.data if j.get('hipodromos') and 'Valparaíso' in j['hipodromos']['nombre']]
if valpo_feb1:
    print(f"⚠️ Jornada del 1 de febrero existe:")
    for j in valpo_feb1:
        print(f"  Jornada ID: {j['id']}")
        
        # Check carreras
        carreras_feb1 = client.get_client().table('carreras')\
            .select('id, numero')\
            .eq('jornada_id', j['id'])\
            .execute()
        
        print(f"  Total carreras: {len(carreras_feb1.data)}")
        
        if carreras_feb1.data:
            race_ids_feb1 = [c['id'] for c in carreras_feb1.data]
            
            # Check predictions
            preds_feb1 = client.get_client().table('predicciones')\
                .select('carrera_id')\
                .in_('carrera_id', race_ids_feb1)\
                .execute()
            
            print(f"  Predicciones asociadas: {len(preds_feb1.data)}")
            
            if len(preds_feb1.data) > 0:
                print("  🚨 PROBLEMA: Hay predicciones del 1 de febrero")
                print("     Estas NO deberían mostrarse en el frontend porque fecha < hoy")
else:
    print("✅ No hay jornada del 1 de febrero para Valparaíso")

print("\n" + "="*70)
print("✅ VERIFICACIÓN COMPLETADA")
print("="*70)
