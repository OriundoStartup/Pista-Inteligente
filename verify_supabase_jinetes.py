"""
Script temporal para verificar estadísticas de jinetes en Supabase.
"""
import os
import sys
sys.path.append(os.path.dirname(__file__))

from src.utils.supabase_client import SupabaseManager

def main():
    client = SupabaseManager()
    supabase = client.get_client()
    
    if not supabase:
        print("❌ No se pudo conectar a Supabase")
        return
    
    # 1. Verificar participaciones con posiciones
    print("\n=== VERIFICANDO DATOS EN SUPABASE ===\n")
    
    # Contar participaciones
    count_res = supabase.table('participaciones').select('*', count='exact', head=True).execute()
    print(f"📦 Total participaciones: {count_res.count}")
    
    # 2. Consultar participaciones con posición = 1 (ganadores)
    winners_res = supabase.table('participaciones').select('*', count='exact', head=True).eq('posicion', 1).execute()
    print(f"🏆 Total ganadores (posicion=1): {winners_res.count}")
    
    # 3. Contar jinetes
    jinetes_res = supabase.table('jinetes').select('*', count='exact', head=True).execute()
    print(f"🏇 Total jinetes: {jinetes_res.count}")
    
    # 4. Obtener muestra de jinetes
    print("\n--- Muestra de jinetes en Supabase ---")
    sample = supabase.table('jinetes').select('id, nombre').limit(10).execute()
    for j in sample.data:
        print(f"  ID: {j['id']}, Nombre: {j['nombre']}")
    
    # 5. Verificar jornadas de 2026
    print("\n--- Jornadas de 2026 ---")
    jornadas_2026 = supabase.table('jornadas').select('id, fecha, hipodromo_id').gte('fecha', '2026-01-01').order('fecha').execute()
    print(f"📅 Jornadas en 2026: {len(jornadas_2026.data)}")
    for j in jornadas_2026.data[:5]:
        print(f"  Jornada ID: {j['id']}, Fecha: {j['fecha']}, Hipódromo: {j['hipodromo_id']}")
    
    # 6. Intentar la misma consulta que hace el frontend
    print("\n--- Simulando consulta del Frontend ---")
    try:
        data = supabase.from_('participaciones').select(
            'posicion, jinetes(nombre), carreras!inner(jornadas!inner(fecha))'
        ).gte('carreras.jornadas.fecha', '2026-01-01').execute()
        
        print(f"📊 Filas obtenidas: {len(data.data)}")
        
        if len(data.data) > 0:
            # Agregar estadísticas
            stats = {}
            for row in data.data:
                jinete_name = row.get('jinetes', {})
                if jinete_name:
                    nombre = jinete_name.get('nombre', 'Desconocido')
                else:
                    nombre = 'Desconocido'
                
                if nombre not in stats:
                    stats[nombre] = {'ganadas': 0, 'montes': 0}
                
                stats[nombre]['montes'] += 1
                if row.get('posicion') == 1:
                    stats[nombre]['ganadas'] += 1
            
            # Ordenar y mostrar Top 5
            top_list = []
            for nombre, s in stats.items():
                eff = (s['ganadas'] / s['montes'] * 100) if s['montes'] > 0 else 0
                top_list.append({
                    'jinete': nombre,
                    'ganadas': s['ganadas'],
                    'eficiencia': round(eff, 1)
                })
            
            top_list.sort(key=lambda x: x['ganadas'], reverse=True)
            
            print("\n🏆 TOP 5 JINETES 2026 (Desde Supabase):")
            for i, j in enumerate(top_list[:5], 1):
                print(f"  {i}. {j['jinete']}: {j['ganadas']} triunfos, {j['eficiencia']}% eficiencia")
        else:
            print("⚠️ No se obtuvieron datos de participaciones 2026")
            
    except Exception as e:
        print(f"❌ Error en consulta del frontend: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
