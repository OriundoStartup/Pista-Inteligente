import os
import sys
sys.path.append(os.path.abspath('.'))

from src.utils.supabase_client import SupabaseManager

db = SupabaseManager()
client = db.get_client()

print("Testing new limits...")

# Test with limit(10000)
result = client.table('predicciones').select(
    '*,'
    'carreras!inner(numero, jornadas!inner(fecha, hipodromos!inner(nombre)))'
).limit(10000).execute()

print(f"Total predictions retrieved: {len(result.data or [])}")

# Count Feb 7
feb7_count = sum(1 for p in (result.data or []) if p.get('carreras', {}).get('jornadas', {}).get('fecha') == '2026-02-07')
print(f"Feb 7 predictions: {feb7_count}")

# Check some Feb 7 samples
if feb7_count > 0:
    print("\n✅ Feb 7 data IS being retrieved now!")
    sample = next(p for p in result.data if p.get('carreras', {}).get('jornadas', {}).get('fecha') == '2026-02-07')
    print(f"Sample: Carrera {sample.get('carreras', {}).get('numero')}, Caballo: {sample.get('caballo')}")
else:
    print("\n❌ Feb 7 data still NOT being retrieved")
