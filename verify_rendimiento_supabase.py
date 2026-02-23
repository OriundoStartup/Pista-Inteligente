import os
import sys
sys.path.append(os.path.abspath('.'))

from src.utils.supabase_client import SupabaseManager

db = SupabaseManager()
client = db.get_client()

print("=" * 60)
print("VERIFICANDO RENDIMIENTO_HISTORICO EN SUPABASE")
print("=" * 60)

# Check total records
result = client.table('rendimiento_historico').select('*', count='exact').execute()
total = result.count

print(f"\n📊 Total de registros: {total}")

# Check 2026 records
result_2026 = client.table('rendimiento_historico').select('fecha', count='exact').gte('fecha', '2026-01-01').execute()
total_2026 = result_2026.count

print(f"📅 Registros 2026: {total_2026}")

# Get some recent records
recent = client.table('rendimiento_historico').select('*').order('fecha', desc=True).limit(10).execute()

if recent.data:
    print(f"\n✅ Últimos 10 registros:\n")
    for r in recent.data:
        status = "✅" if (r.get('acierto_ganador') or r.get('acierto_quiniela') or r.get('acierto_trifecta') or r.get('acierto_superfecta')) else "❌"
        print(f"{status} {r['fecha']} - {r['hipodromo']} C{r['nro_carrera']}")
else:
    print("\n❌ No hay registros en rendimiento_historico")

# Check rendimiento_stats
stats = client.table('rendimiento_stats').select('*').eq('id', 'global_stats').execute()
if stats.data:
    print(f"\n📈 Global stats actualizado")
else:
    print(f"\n⚠️ Global stats no encontrado")
