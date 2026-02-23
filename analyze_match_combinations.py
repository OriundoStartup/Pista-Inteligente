import os
import sys
sys.path.append(os.path.abspath('.'))

from src.utils.supabase_client import SupabaseManager

db = SupabaseManager()
client = db.get_client()

print("=" * 70)
print("ANÁLISIS DE TIPOS DE ACIERTOS")
print("=" * 70)

# Get all 2026 races with at least one match
or_filter = 'acierto_ganador.eq.true,acierto_quiniela.eq.true,acierto_trifecta.eq.true,acierto_superfecta.eq.true'
result = client.table('rendimiento_historico').select('*').gte('fecha', '2026-01-01').or_(or_filter).execute()

races_with_matches = result.data or []

print(f"\n📊 Total carreras con al menos 1 acierto: {len(races_with_matches)}")

# Analyze combinations
superfecta_list = []
trifecta_list = []
quiniela_list = []
ganador_list = []

for r in races_with_matches:
    types = []
    if r.get('acierto_superfecta'):
        types.append('SUPER')
    if r.get('acierto_trifecta'):
        types.append('TRI')
    if r.get('acierto_quiniela'):
        types.append('QUIN')
    if r.get('acierto_ganador'):
        types.append('GAN')
    
    combo = '+'.join(types)
    
    fecha = r.get('fecha')
    hip = r.get('hipodromo', '')[:20]
    nro = r.get('nro_carrera')
    entry = f"{fecha} {hip:20} C{nro:2}: {combo}"
    
    if r.get('acierto_superfecta'):
        superfecta_list.append(entry)
    elif r.get('acierto_trifecta'):
        trifecta_list.append(entry)
    elif r.get('acierto_quiniela'):
        quiniela_list.append(entry)
    elif r.get('acierto_ganador'):
        ganador_list.append(entry)

print(f"\n🏆 SUPERFECTAS ({len(superfecta_list)}):")
for s in superfecta_list:
    print(f"  {s}")

print(f"\n🥉 TRIFECTAS (sin super) ({len(trifecta_list)}):")
for t in trifecta_list:
    print(f"  {t}")

print(f"\n🥈 QUINIELAS (sin tri/super) ({len(quiniela_list)}):")
for q in quiniela_list:
    print(f"  {q}")

print(f"\n🥇 SOLO GANADOR ({len(ganador_list)}):")
for g in ganador_list[:5]:
    print(f"  {g}")
if len(ganador_list) > 5:
    print(f"  ... y {len(ganador_list) - 5} más")
