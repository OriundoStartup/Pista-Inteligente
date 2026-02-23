import os
import sys
sys.path.append(os.path.abspath('.'))

from src.utils.supabase_client import SupabaseManager

db = SupabaseManager()
client = db.get_client()

print("=" * 60)
print("INVESTIGANDO FEBRERO 7, 2026 - CARRERA 5")
print("=" * 60)

# Check rendimiento_historico for Feb 7
result = client.table('rendimiento_historico').select('*').eq('fecha', '2026-02-07').execute()

if not result.data:
    print("\n❌ No hay datos de rendimiento para 2026-02-07")
    print("\nPosibles causas:")
    print("1. Los resultados del 7 de febrero no están en SQLite")
    print("2. Las predicciones del 7 de febrero no están en Supabase")
    print("3. El matching no se ejecutó correctamente")
else:
    print(f"\n✅ Encontrados {len(result.data)} registros para 2026-02-07\n")
    
    # Check carrera 5 specifically
    carrera_5 = [r for r in result.data if r['nro_carrera'] == 5]
    
    if carrera_5:
        for r in carrera_5:
            print(f"📍 Carrera 5 - {r['hipodromo']}:")
            print(f"   Ganador: {'✅' if r['acierto_ganador'] else '❌'}")
            print(f"   Quiniela: {'✅' if r['acierto_quiniela'] else '❌'}")
            print(f"   Trifecta: {'✅' if r['acierto_trifecta'] else '❌'}")
            print(f"   Superfecta: {'✅' if r['acierto_superfecta'] else '❌'}")
            
            if 'prediccion_top4' in r and 'resultado_top4' in r:
                import json
                pred = r['prediccion_top4'] if isinstance(r['prediccion_top4'], list) else json.loads(r['prediccion_top4'])
                res = r['resultado_top4'] if isinstance(r['resultado_top4'], list) else json.loads(r['resultado_top4'])
                
                print(f"\n   🤖 Predicción: {pred[:4]}")
                print(f"   🏁 Resultado:  {res[:4]}")
    else:
        print("\n❌ No se encontró la carrera 5 para 2026-02-07")
        print("\nCarreras disponibles:")
        for r in result.data:
            print(f"  - Carrera {r['nro_carrera']}: {r['hipodromo']}")

# Also check all Feb 2026 races with aciertos
print("\n" + "=" * 60)
print("TODOS LOS ACIERTOS EN FEBRERO 2026")
print("=" * 60)

feb_result = client.table('rendimiento_historico').select('*').gte('fecha', '2026-02-01').lte('fecha', '2026-02-28').execute()

if feb_result.data:
    with_aciertos_feb = [r for r in feb_result.data if (
        r.get('acierto_ganador') or 
        r.get('acierto_quiniela') or 
        r.get('acierto_trifecta') or 
        r.get('acierto_superfecta')
    )]
    
    if with_aciertos_feb:
        print(f"\n✅ Encontradas {len(with_aciertos_feb)} carreras con aciertos en febrero:\n")
        for r in with_aciertos_feb:
            tipos = []
            if r.get('acierto_ganador'): tipos.append('🥇 Ganador')
            if r.get('acierto_quiniela'): tipos.append('🎯 Quiniela')
            if r.get('acierto_trifecta'): tipos.append('🏆 Trifecta')
            if r.get('acierto_superfecta'): tipos.append('⭐ Superfecta')
            
            print(f"  {r['fecha']} - {r['hipodromo']} C{r['nro_carrera']}")
            print(f"    {', '.join(tipos)}")
    else:
        print(f"\n❌ No hay carreras con aciertos en febrero 2026")
else:
    print(f"\n❌ No hay datos de febrero 2026")
