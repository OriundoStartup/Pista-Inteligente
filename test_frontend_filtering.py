"""Test script to verify frontend query behavior"""
from src.utils.supabase_client import SupabaseManager
from datetime import datetime
import pytz

client = SupabaseManager()
chile_tz = pytz.timezone('America/Santiago')
today = datetime.now(chile_tz).strftime('%Y-%m-%d')

print("="*70)
print("TESTING FRONTEND QUERY LOGIC")
print("="*70)
print(f"\nToday (Chile time): {today}")

# Get Valparaiso ID
hip_res = client.get_client().table('hipodromos').select('id, nombre').execute()
valpo = [h for h in hip_res.data if 'Valpara' in h['nombre']][0]
valpo_id = valpo['id']

# Simulate frontend query
print("\nStep 1: Get future jornadas (fecha >= today)")
jornadas = client.get_client().table('jornadas')\
    .select('id, fecha, hipodromo_id')\
    .eq('hipodromo_id', valpo_id)\
    .gte('fecha', today)\
    .order('fecha')\
    .limit(5)\
    .execute()

print(f"Found {len(jornadas.data)} jornadas:")
for j in jornadas.data:
    print(f"  - {j['fecha']} (ID: {j['id']})")

if not jornadas.data:
    print("\nNo future jornadas found - NOTHING WILL SHOW IN FRONTEND")
    exit(0)

# Get carreras
print("\nStep 2: Get all carreras for these jornadas")
jornada_ids = [j['id'] for j in jornadas.data]
carreras = client.get_client().table('carreras')\
    .select('id, numero, jornada_id')\
    .in_('jornada_id', jornada_ids)\
    .execute()

print(f"Total carreras: {len(carreras.data)}")

# Get results
print("\nStep 3: Filter out completed races")
all_race_ids = [c['id'] for c in carreras.data]
results = client.get_client().table('participaciones')\
    .select('carrera_id')\
    .in_('carrera_id', all_race_ids)\
    .execute()

completed_set = set([r['carrera_id'] for r in results.data])
print(f"Races with results (will be hidden): {len(completed_set)}")

# NEW FILTERING LOGIC (matching frontend fix)
print("\nStep 4: Apply NEW double filtering")
active_carreras = []
filtered_by_date = 0

for c in carreras.data:
    # Check if race has results
    if c['id'] in completed_set:
        continue
    
    # Check if race is from past jornada
    jornada = next((j for j in jornadas.data if j['id'] == c['jornada_id']), None)
    if jornada and jornada['fecha'] < today:
        filtered_by_date += 1
        continue
    
    active_carreras.append(c)

print(f"Filtered by date (past races): {filtered_by_date}")
print(f"Active races to show: {len(active_carreras)}")

# Group by date
from collections import defaultdict
by_date = defaultdict(list)
for c in active_carreras:
    jornada = next((j for j in jornadas.data if j['id'] == c['jornada_id']), None)
    if jornada:
        by_date[jornada['fecha']].append(c['numero'])

print("\nRACES THAT WILL SHOW IN FRONTEND:")
if not by_date:
    print("  NONE - Perfect!")
else:
    for fecha, nums in sorted(by_date.items()):
        print(f"  {fecha}: {len(nums)} carreras - {sorted(nums)}")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)
