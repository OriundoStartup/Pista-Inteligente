
import os
import sys
sys.path.append(os.path.abspath('.'))
from src.utils.supabase_client import SupabaseManager

def main():
    client = SupabaseManager()
    supabase = client.get_client()
    
    # 1. Get Top Jinetes names first
    print("=== OBTENIENDO TOP JINETES 2026 (RPC) ===")
    rpc_res = supabase.rpc('get_top_jinetes_2026', {}).execute()
    
    if not rpc_res.data:
        print("❌ RPC retornó vacío")
        return

    top_3 = rpc_res.data[:3]
    
    print(f"\nAuditando detalles para el Top 3: {[j['jinete'] for j in top_3]}")
    print("="*60)
    
    for jinete in top_3:
        nombre = jinete['jinete']
        wins = jinete['ganadas']
        
        print(f"\n🏇 JINETE: {nombre} | Total Triunfos reportados: {wins}")
        print("-" * 60)
        
        # 2. Fetch details for this jockey in 2026
        # Need to join: participaciones -> jinetes & participaciones -> carreras -> jornadas
        # Supabase API complex join
        
        # We find the jinete_id first to be safe or filter by name in inner join if possible.
        # Let's try filtering by name directly in the nested query if permitted, or get ID first.
        
        # Get ID
        j_res = supabase.table('jinetes').select('id').eq('nombre', nombre).limit(1).execute()
        if not j_res.data:
            print(f"⚠️ No se encontró ID para {nombre}")
            continue
            
        j_id = j_res.data[0]['id']
        
        # Get victories Details
        # participaciones (posicion=1, jinete_id=X) -> carreras -> jornadas (fecha 2026)
        
        # Note: 'carreras' implies inner join by default in logic but API needs !inner for filtering AND ensuring data existence.
        det_res = supabase.table('participaciones').select(
            'posicion, carreras!inner(numero, jornadas!inner(fecha, hipodromos!inner(nombre)))'
        )\
        .eq('jinete_id', j_id)\
        .eq('posicion', 1)\
        .gte('carreras.jornadas.fecha', '2026-01-01')\
        .lte('carreras.jornadas.fecha', '2026-12-31')\
        .execute()
        
        stat_rows = det_res.data if det_res.data else []
        
        # Sort in Python with safety checks
        def get_date(x):
            c = x.get('carreras') or {}
            j = c.get('jornadas') or {}
            return j.get('fecha', '')
            
        stat_rows.sort(key=get_date, reverse=True)
        
        print(f"   ✅ Registros encontrados individuales: {len(stat_rows)}")
        if len(stat_rows) != wins:
             print(f"   ⚠️ WARNING: Discrepancia RPC ({wins}) vs Detalle ({len(stat_rows)}).")
        
        # Print sample dates to verify 2026
        dates_seen = []
        print("   📜 Últimas 5 Victorias:")
        for r in stat_rows[:5]:
            carrera = r.get('carreras', {})
            jornada = carrera.get('jornadas', {})
            hipodromo = jornada.get('hipodromos', {})
            
            fecha = jornada.get('fecha', 'N/A')
            hip_nombre = hipodromo.get('nombre', 'N/A')
            nro = carrera.get('numero', '?')
            
            print(f"      • {fecha} | {hip_nombre} | Carrera {nro}")
            dates_seen.append(fecha)
            
        # Verify Year
        bad_dates = [d for d in dates_seen if not d.startswith('2026')]
        if bad_dates:
             print(f"   ❌ ALERTA: Fechas fuera de 2026 detectadas: {bad_dates}")
        else:
             print("   ✅ Todas las fechas verificadas corresponden a 2026.")

if __name__ == "__main__":
    main()
