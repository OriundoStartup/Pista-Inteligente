import os
import sys
sys.path.append(os.path.abspath('.'))

from src.utils.supabase_client import SupabaseManager

db = SupabaseManager()
client = db.get_client()

print("=" * 70)
print("VERIFICANDO TRIFECTA DEL 7 DE FEBRERO ESPECÍFICAMENTE")
print("=" * 70)

# Get Feb 7 Race 5
result = client.table('rendimiento_historico').select('*').eq('fecha', '2026-02-07').eq('nro_carrera', 5).execute()

if result.data and len(result.data) > 0:
    r = result.data[0]
    print(f"\n✅ ENCONTRADA: Feb 7, Carrera 5")
    print(f"Hipódromo: {r.get('hipodromo')}")
    print(f"Predicción Top 4: {r.get('prediccion_top4')}")
    print(f"Resultado Top 4: {r.get('resultado_top4')}")
    print(f"\nAciertos:")
    print(f"  🥇 Ganador: {'✅' if r.get('acierto_ganador') else '❌'}")
    print(f"  🥈 Quiniela: {'✅' if r.get('acierto_quiniela') else '❌'}")
    print(f"  🥉 Trifecta: {'✅✅✅' if r.get('acierto_trifecta') else '❌'}")
    print(f"  🏆 Superfecta: {'✅' if r.get('acierto_superfecta') else '❌'}")
else:
    print(f"\n❌ NO ENCONTRADA en rendimiento_historico")
    
# Also check ALL Feb 7 races
print(f"\n" + "=" * 70)
print("TODAS LAS CARRERAS DEL 7 DE FEBRERO")
print("=" * 70)

all_feb7 = client.table('rendimiento_historico').select('*').eq('fecha', '2026-02-07').execute()

print(f"\nTotal carreras del 7 de feb en rendimiento_historico: {len(all_feb7.data or [])}")

for r in (all_feb7.data or []):
    types = []
    if r.get('acierto_superfecta'): types.append('SUPER')
    if r.get('acierto_trifecta'): types.append('TRI')
    if r.get('acierto_quiniela'): types.append('QUIN')
    if r.get('acierto_ganador'): types.append('GAN')
    combo = '+'.join(types) if types else 'SIN ACIERTO'
    
    hip = r.get('hipodromo', '')[:20]
    nro = r.get('nro_carrera')
    print(f"  C{nro:2} {hip:20}: {combo}")
