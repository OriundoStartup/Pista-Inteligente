"""Fix: Actualizar distancia usando datos corregidos de programa_carreras"""
import sqlite3
from src.utils.supabase_client import SupabaseManager

def update_carreras_with_distancia():
    db = SupabaseManager()
    client = db.get_client()
    
    # Get all carreras without distancia
    res = client.table('carreras').select('id, numero, jornada_id').is_('distancia', 'null').execute()
    carreras = res.data
    
    print(f"Found {len(carreras)} carreras without distancia")
    
    if not carreras:
        print("All carreras have distancia!")
        return
    
    # Get jornadas
    jornadas = client.table('jornadas').select('id, fecha').execute()
    jornada_map = {j['id']: j['fecha'] for j in jornadas.data}
    
    # Connect to SQLite
    conn = sqlite3.connect('data/db/hipica_data.db')
    cur = conn.cursor()
    
    updated = 0
    for c in carreras:
        fecha = jornada_map.get(c['jornada_id'])
        if not fecha:
            continue
        
        # Get distancia from programa_carreras (already fixed)
        cur.execute("""
            SELECT distancia FROM programa_carreras 
            WHERE fecha = ? AND nro_carrera = ?
            LIMIT 1
        """, (fecha, c['numero']))
        
        result = cur.fetchone()
        if result and result[0]:
            distancia = result[0]
            # Si es entero, usarlo directo
            if isinstance(distancia, int):
                dist_int = distancia
            else:
                # Limpiar string
                s = str(distancia).replace('m', '').replace('M', '').strip()
                if '.' in s:
                    parts = s.split('.')
                    if len(parts) == 2 and len(parts[1]) == 3:
                        s = s.replace('.', '')
                try:
                    dist_int = int(s)
                except:
                    continue
            
            if dist_int and dist_int > 100:  # Sanity check
                client.table('carreras').update({'distancia': dist_int}).eq('id', c['id']).execute()
                print(f"  ✅ C{c['numero']} ({fecha}): distancia={dist_int}")
                updated += 1
    
    conn.close()
    print(f"\n✅ Updated {updated} carreras with distancia")

if __name__ == "__main__":
    update_carreras_with_distancia()
