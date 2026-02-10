
import os
import sys
sys.path.append(os.path.abspath('.'))

from src.utils.supabase_client import SupabaseManager

db = SupabaseManager()
client = db.get_client()

print("Verifying predictions for 2026-02-09...")

# Query specifically for this date
# We need to join with carreras -> jornadas -> fecha
# But Supabase select syntax with filters on joined tables is tricky.
# Instead, step 1: Get carreras for Feb 9.
# Step 2: Get predictions for those carreras.

# 1. Get carreras for Feb 9
# We search jornadas first
jornadas = client.table('jornadas').select('id, fecha').eq('fecha', '2026-02-09').execute().data
print(f"Jornadas found: {len(jornadas)}")

if not jornadas:
    print("No jornadas found for 2026-02-09")
    sys.exit(0)

jornada_ids = [j['id'] for j in jornadas]

# Get carreras
carreras = client.table('carreras').select('id, numero').in_('jornada_id', jornada_ids).execute().data
print(f"Carreras found: {len(carreras)}")

if not carreras:
    print("No carreras found")
    sys.exit(0)

carrera_ids = [c['id'] for c in carreras]

# 2. Get predictions
preds_response = client.table('predicciones').select('*', count='exact').in_('carrera_id', carrera_ids).execute()
preds = preds_response.data
count = preds_response.count

print(f"Predictions found: {len(preds)}")
print(f"Total count (from DB): {count}")

if preds:
    print("Sample prediction:")
    print(preds[0])
