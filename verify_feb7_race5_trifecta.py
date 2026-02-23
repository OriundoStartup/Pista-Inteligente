import os
import sys
sys.path.append(os.path.abspath('.'))

from src.utils.supabase_client import SupabaseManager

db = SupabaseManager()
client = db.get_client()

print("=" * 60)
print("VERIFICANDO TRIFECTA DEL 7 DE FEBRERO - CARRERA 5")
print("=" * 60)

# Get Feb 7, Race 5 from rendimiento_historico
result = client.table('rendimiento_historico').select('*').eq('fecha', '2026-02-07').eq('nro_carrera', 5).execute()

if result.data:
    for r in result.data:
        print(f"\n✅ ¡ENCONTRADA!")
        print(f"Fecha: {r['fecha']}")
        print(f"Hipódromo: {r['hipodromo']}")
        print(f"Carrera: {r['nro_carrera']}")
        print(f"Acierto Ganador: {'✅' if r.get('acierto_ganador') else '❌'}")
        print(f"Acierto Quiniela: {'✅' if r.get('acierto_quiniela') else '❌'}")
        print(f"Acierto Trifecta: {'✅✅✅' if r.get('acierto_trifecta') else '❌'}")
        print(f"Acierto Superfecta: {'✅' if r.get('acierto_superfecta') else '❌'}")
        print(f"\nPredicción Top 4: {r.get('prediccion_top4')}")
        print(f"Resultado Top 4: {r.get('resultado_top4')}")
else:
    print("\n❌ No se encontró la carrera 5 del 7 de febrero")
