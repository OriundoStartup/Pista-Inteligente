import os
import sys
sys.path.append(os.path.abspath('.'))

from src.utils.supabase_client import SupabaseManager

db = SupabaseManager()
client = db.get_client()

print("=" * 60)
print("ANÁLISIS COMPLETO DE ACIERTOS EN RENDIMIENTO_HISTORICO")
print("=" * 60)

# Get all records from rendimiento_historico
result = client.table('rendimiento_historico').select('*').execute()

if not result.data:
    print("\n❌ No hay datos en rendimiento_historico")
else:
    total = len(result.data)
    print(f"\n📊 Total registros: {total}")
    
    # Count by type of match
    ganador = sum(1 for r in result.data if r.get('acierto_ganador'))
    quiniela = sum(1 for r in result.data if r.get('acierto_quiniela'))
    trifecta = sum(1 for r in result.data if r.get('acierto_trifecta'))
    superfecta = sum(1 for r in result.data if r.get('acierto_superfecta'))
    
    print(f"\n🎯 ACIERTOS POR TIPO:")
    print(f"  🥇 Ganador: {ganador}")
    print(f"  🥈 Quiniela: {quiniela}")
    print(f"  🥉 Trifecta: {trifecta}")
    print(f"  🏆 Superfecta: {superfecta}")
    
    # Show all matches in detail
    print(f"\n📋 DETALLE DE TODOS LOS ACIERTOS:\n")
    
    count = 0
    for r in result.data:
        has_match = (r.get('acierto_ganador') or r.get('acierto_quiniela') or 
                     r.get('acierto_trifecta') or r.get('acierto_superfecta'))
        
        if has_match:
            count += 1
            fecha = r.get('fecha')
            hip = r.get('hipodromo')
            nro = r.get('nro_carrera')
            
            matches = []
            if r.get('acierto_superfecta'):
                matches.append('🏆 SUPERFECTA')
            if r.get('acierto_trifecta'):
                matches.append('🥉 TRIFECTA')
            if r.get('acierto_quiniela'):
                matches.append('🥈 QUINIELA')
            if r.get('acierto_ganador'):
                matches.append('🥇 GANADOR')
            
            print(f"{count}. {fecha} - {hip} C{nro}")
            print(f"   {' + '.join(matches)}")
            print(f"   Predicción: {r.get('prediccion_top4')}")
            print(f"   Resultado:  {r.get('resultado_top4')}")
            print()
    
    print(f"\n✅ TOTAL CARRERAS CON ACIERTOS: {count}")
    
    # Check specifically Feb 2026
    feb_2026 = [r for r in result.data if r.get('fecha', '').startswith('2026-02')]
    feb_matches = sum(1 for r in feb_2026 if (r.get('acierto_ganador') or r.get('acierto_quiniela') or 
                                               r.get('acierto_trifecta') or r.get('acierto_superfecta')))
    
    print(f"\n📅 FEBRERO 2026:")
    print(f"  Total carreras: {len(feb_2026)}")
    print(f"  Carreras con aciertos: {feb_matches}")
