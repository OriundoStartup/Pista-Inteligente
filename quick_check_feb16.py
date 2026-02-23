"""Quick check for Feb 16 Valparaiso"""
from src.utils.supabase_client import SupabaseManager

client = SupabaseManager().get_client()

# Get Valparaiso hipódromo ID
hip_res = client.table('hipodromos').select('id, nombre').execute()
valpo = [h for h in hip_res.data if 'Valpara' in h['nombre']][0]
valpo_id = valpo['id']

print(f"Hipodromo: {valpo['nombre']} (ID: {valpo_id})")

# Get jornadas for Feb 16
jorn_res = client.table('jornadas')\
    .select('id, fecha')\
    .eq('hipodromo_id', valpo_id)\
    .eq('fecha', '2026-02-16')\
    .execute()

print(f"\nJornadas para 2026-02-16: {len(jorn_res.data)}")

if len(jorn_res.data) > 1:
    print("PROBLEMA: Multiples jornadas para la misma fecha!")
    for j in jorn_res.data:
        print(f"  Jornada ID: {j['id']}")

for jornada in jorn_res.data:
    jid = jornada['id']
    print(f"\nJornada ID: {jid}")
    
    # Get carreras
    car_res = client.table('carreras')\
        .select('id, numero')\
        .eq('jornada_id', jid)\
        .order('numero')\
        .execute()
    
    numeros = [c['numero'] for c in car_res.data]
    print(f"Total carreras: {len(numeros)}")
    print(f"Numeros: {numeros}")
    
    # Check duplicates
    dup = [n for n in set(numeros) if numeros.count(n) > 1]
    if dup:
        print(f"DUPLICADOS: {dup}")
