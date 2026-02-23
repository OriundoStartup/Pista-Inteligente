import os
import sys
sys.path.append(os.path.abspath('.'))

from src.utils.supabase_client import SupabaseManager

db = SupabaseManager()
client = db.get_client()

print("=" * 70)
print("QUERY EXACTA QUE USA EL FRONTEND")
print("=" * 70)

# Exactly the same query as frontend
result = client.table('rendimiento_historico') \
    .select('*') \
    .gte('fecha', '2026-01-01') \
    .or_('acierto_ganador.eq.true,acierto_quinelaI.eq.true,acierto_trifecta.eq.true,acierto_superfecta.eq.true') \
    .order('fecha', desc=True) \
    .limit(100) \
    .execute()

print(f"\nTotal races fetched: {len(result.data or [])}")

# Count by type
ganador = 0
quiniela = 0
trifecta = 0
superfecta = 0

for r in (result.data or []):
    if r.get('acierto_ganador'):
        ganador += 1
    if r.get('acierto_quiniela'):
        quiniela += 1
    if r.get('acierto_trifecta'):
        trifecta += 1
    if r.get('acierto_superfecta'):
        superfecta += 1

print(f"\nTypes in fetched data:")
print(f"  Ganador: {ganador}")
print(f"  Quiniela: {quiniela}")
print(f"  Trifecta: {trifecta}")
print(f"  Superfecta: {superfecta}")

# Show some examples
print(f"\nFirst 3 races:")
for r in (result.data or [])[:3]:
    types = []
    if r.get('acierto_superfecta'): types.append('SUPER')
    if r.get('acierto_trifecta'): types.append('TRI')
    if r.get('acierto_quiniela'): types.append('QUIN')
    if r.get('acierto_ganador'): types.append('GAN')
    combo = '+'.join(types) if types else 'NONE'
    print(f"  {r.get('fecha')} {r.get('hipodromo')[:20]:20} C{r.get('nro_carrera'):2}: {combo}")
