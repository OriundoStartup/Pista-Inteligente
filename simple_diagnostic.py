"""Simple diagnostic - ASCII only"""
from src.utils.supabase_client import SupabaseManager
from datetime import datetime
import pytz

client = SupabaseManager()
chile_tz = pytz.timezone('America/Santiago')
today = datetime.now(chile_tz).strftime('%Y-%m-%d')

print("="*70)
print(f"DIAGNOSTIC - Today: {today}")
print("="*70)

# Get Valparaiso ID
hip_res = client.get_client().table('hipodromos').select('id, nombre').execute()
valpo = [h for h in hip_res.data if 'Valpara' in h['nombre']][0]
valpo_id = valpo['id']
print(f"\nHipodromo ID: {valpo_id}")

# Check Feb 1
print("\n1. Feb 1, 2026:")
j1 = client.get_client().table('jornadas').select('id').eq('hipodromo_id', valpo_id).eq('fecha', '2026-02-01').execute()
if j1.data:
    jid = j1.data[0]['id']
    print(f"   Jornada ID: {jid}")
    
    # Get races
    races = client.get_client().table('carreras').select('id').eq('jornada_id', jid).execute()
    race_ids = [r['id'] for r in races.data]
    print(f"   Total races: {len(race_ids)}")
    
    # Check results
    results = client.get_client().table('participaciones').select('carrera_id').in_('carrera_id', race_ids).execute()
    with_results = set([r['carrera_id'] for r in results.data])
    without_results = [rid for rid in race_ids if rid not in with_results]
    
    print(f"   Races WITH results: {len(with_results)}")
    print(f"   Races WITHOUT results: {len(without_results)}")
    
    if without_results:
        print(f"   PROBLEM: {len(without_results)} races from Feb 1 have no results!")
        print(f"   These will appear as 'active' in frontend")

# Check Feb 16
print("\n2. Feb 16, 2026:")
j16 = client.get_client().table('jornadas').select('id').eq('hipodromo_id', valpo_id).eq('fecha', '2026-02-16').execute()
if j16.data:
    jid = j16.data[0]['id']
    print(f"   Jornada ID: {jid}")
    
    # Get races
    races = client.get_client().table('carreras').select('id').eq('jornada_id', jid).execute()
    print(f"   Total races: {len(races.data)}")
else:
    print("   NO JORNADA FOUND - This is the problem!")

# Simulate frontend query
print("\n3. Frontend query simulation:")
print(f"   Filtering jornadas with fecha >= {today}")

jornadas = client.get_client().table('jornadas')\
    .select('id, fecha')\
    .eq('hipodromo_id', valpo_id)\
    .gte('fecha', today)\
    .order('fecha')\
    .limit(5)\
    .execute()

print(f"   Found {len(jornadas.data)} future jornadas:")
for j in jornadas.data:
    print(f"      - {j['fecha']} (ID: {j['id']})")

print("\n" + "="*70)
print("DIAGNOSTIC COMPLETE")
print("="*70)
