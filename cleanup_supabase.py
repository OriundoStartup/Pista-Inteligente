"""
COMPREHENSIVE FIX: Clean stale 'Club Hípico de S.' data from both SQLite and Supabase.
Steps:
  1. Fix SQLite: normalize hipódromo names and programa_carreras
  2. Clean Supabase: delete stale hipódromo cascade + clean 2026-02-27 data
"""
import sys, os, sqlite3
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from src.utils.supabase_client import SupabaseManager

DB_PATH = 'data/db/hipica_data.db'

def fix_sqlite():
    """Fix abbreviated hipódromo names in SQLite."""
    print("="*60)
    print("PASO 1: CORREGIR SQLite")
    print("="*60)
    
    if not os.path.exists(DB_PATH):
        print(f"   DB no encontrada: {DB_PATH}")
        # Try alternate path
        alt = 'data/hipica.db'
        if os.path.exists(alt):
            print(f"   Usando path alternativo: {alt}")
        else:
            print("   ❌ No se encontró la base de datos SQLite")
            return
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Check current state
    print("\n📋 Estado actual de hipódromos en SQLite:")
    for row in c.execute("SELECT id, nombre FROM hipodromos"):
        print(f"   ID={row[0]}: '{row[1]}'")
    
    # Fix hipodromos: merge duplicates instead of renaming (avoids UNIQUE constraint)
    print("\n🔧 Normalizando hipódromos...")
    
    # Aliases to normalize
    aliases = {
        'Club Hípico de S.': 'Club Hípico de Santiago',
        'Club Hipico de Santiago': 'Club Hípico de Santiago', 
        'Club Hípico de Stgo': 'Club Hípico de Santiago',
        'CLUB HIPICO DE S.': 'Club Hípico de Santiago',
    }
    
    for wrong_name, correct_name in aliases.items():
        # Find both IDs
        c.execute("SELECT id FROM hipodromos WHERE nombre = ?", (wrong_name,))
        wrong_row = c.fetchone()
        c.execute("SELECT id FROM hipodromos WHERE nombre = ?", (correct_name,))
        correct_row = c.fetchone()
        
        if wrong_row:
            wrong_id = wrong_row[0]
            if correct_row:
                # Both exist: merge references then delete duplicate
                correct_id = correct_row[0]
                print(f"   Merging '{wrong_name}' (ID={wrong_id}) -> '{correct_name}' (ID={correct_id})")
                c.execute("UPDATE jornadas SET hipodromo_id = ? WHERE hipodromo_id = ?", (correct_id, wrong_id))
                c.execute("DELETE FROM hipodromos WHERE id = ?", (wrong_id,))
            else:
                # Only wrong exists: just rename
                print(f"   Renaming '{wrong_name}' (ID={wrong_id}) -> '{correct_name}'")
                c.execute("UPDATE hipodromos SET nombre = ? WHERE id = ?", (correct_name, wrong_id))
    
    print(f"   ✅ Hipódromos normalizados")
    
    # Fix programa_carreras: DELETE abbreviated entries (correct ones already exist from CSV fix)
    print("\n🔧 Limpiando programa_carreras con nombres abreviados...")
    c.execute("SELECT COUNT(*) FROM programa_carreras WHERE hipodromo = 'Club Hípico de S.'")
    count = c.fetchone()[0]
    print(f"   Registros con 'Club Hípico de S.': {count}")
    c.execute("DELETE FROM programa_carreras WHERE hipodromo = 'Club Hípico de S.'")
    c.execute("DELETE FROM programa_carreras WHERE hipodromo = 'Club Hipico de Santiago'")
    c.execute("DELETE FROM programa_carreras WHERE hipodromo = 'CLUB HIPICO DE S.'")
    print(f"   ✅ Registros abreviados eliminados de programa_carreras")
    
    # Verify
    print("\n📋 Estado corregido de hipódromos en SQLite:")
    for row in c.execute("SELECT id, nombre FROM hipodromos"):
        print(f"   ID={row[0]}: '{row[1]}'")
    
    # Check for duplicate hipodromos (same name, different IDs)
    c.execute("SELECT nombre, COUNT(*), GROUP_CONCAT(id) FROM hipodromos GROUP BY nombre HAVING COUNT(*) > 1")
    dupes = c.fetchall()
    if dupes:
        print("\n⚠️ Hipódromos duplicados encontrados:")
        for name, count, ids in dupes:
            print(f"   '{name}': {count} entradas (IDs: {ids})")
            # Keep the lowest ID, update references for others
            id_list = [int(x) for x in ids.split(',')]
            keep_id = min(id_list)
            remove_ids = [x for x in id_list if x != keep_id]
            print(f"   Manteniendo ID={keep_id}, eliminando IDs={remove_ids}")
            for rid in remove_ids:
                # Update jornadas that reference the duplicate
                c.execute("UPDATE jornadas SET hipodromo_id = ? WHERE hipodromo_id = ?", (keep_id, rid))
                c.execute("DELETE FROM hipodromos WHERE id = ?", (rid,))
            print(f"   ✅ Duplicados resueltos")
    
    # Also clean the archivos_procesados to force re-processing
    try:
        c.execute("DELETE FROM archivos_procesados WHERE nombre_archivo LIKE '%CHC_2026-02-27%'")
        print(f"\n🗑️ Tracking de archivo CHC_2026-02-27 limpiado para re-procesamiento")
    except:
        pass
    
    conn.commit()
    conn.close()
    print("\n✅ SQLite corregido")


def fix_supabase():
    """Clean stale data from Supabase."""
    print("\n" + "="*60)
    print("PASO 2: LIMPIAR SUPABASE")
    print("="*60)
    
    db = SupabaseManager()
    client = db.get_client()
    if not client:
        print("❌ No se pudo conectar a Supabase")
        return
    
    # 1. Find ALL hipódromos
    print("\n📋 Hipódromos actuales en Supabase:")
    hip_all = client.table('hipodromos').select('id, nombre').execute()
    for h in hip_all.data:
        print(f"   ID={h['id']}: '{h['nombre']}'")
    
    # 2. Find and delete stale hipódromo 'Club Hípico de S.'
    # Match exact name AND partial to catch variants
    stale_names = []
    for h in hip_all.data:
        name = h['nombre']
        if name == 'Club Hípico de S.' or name == 'CLUB HIPICO DE S.' or 'Club Hípico de S.' in name:
            stale_names.append(h)
    
    if not stale_names:
        print("\n   No se encontró 'Club Hípico de S.' como hipódromo separado")
    
    for hip in stale_names:
        hip_id = hip['id']
        hip_name = hip['nombre']
        print(f"\n🗑️ Eliminando hipódromo estancado: '{hip_name}' (ID: {hip_id})")
        
        # Cascade delete: predicciones -> carreras -> jornadas -> hipodromo
        jor_res = client.table('jornadas').select('id').eq('hipodromo_id', hip_id).execute()
        for j in (jor_res.data or []):
            car_res = client.table('carreras').select('id').eq('jornada_id', j['id']).execute()
            for c in (car_res.data or []):
                client.table('predicciones').delete().eq('carrera_id', c['id']).execute()
                client.table('carreras').delete().eq('id', c['id']).execute()
            client.table('jornadas').delete().eq('id', j['id']).execute()
        client.table('hipodromos').delete().eq('id', hip_id).execute()
        print(f"   ✅ Cascade delete completado para '{hip_name}'")
    
    # 3. Clean 2026-02-27 data from correct hipódromo too, so it's re-created fresh
    print("\n🔧 Limpiando datos 2026-02-27 del hipódromo correcto...")
    hip_ok = client.table('hipodromos').select('id').eq('nombre', 'Club Hípico de Santiago').execute()
    if hip_ok.data:
        hip_ok_id = hip_ok.data[0]['id']
        jor_ok = client.table('jornadas').select('id').eq('hipodromo_id', hip_ok_id).eq('fecha', '2026-02-27').execute()
        if jor_ok.data:
            for j in jor_ok.data:
                car_ok = client.table('carreras').select('id').eq('jornada_id', j['id']).execute()
                pred_count = 0
                for c in (car_ok.data or []):
                    p = client.table('predicciones').delete().eq('carrera_id', c['id']).execute()
                    pred_count += len(p.data) if p.data else 0
                    client.table('carreras').delete().eq('id', c['id']).execute()
                client.table('jornadas').delete().eq('id', j['id']).execute()
                print(f"   🗑️ Jornada 2026-02-27: {len(car_ok.data or [])} carreras, {pred_count} predicciones eliminadas")
        else:
            print("   No hay jornada 2026-02-27 (ya limpia)")
    
    # 4. Verify final state
    print("\n📋 Estado final de hipódromos:")
    hip_final = client.table('hipodromos').select('id, nombre').execute()
    for h in hip_final.data:
        print(f"   ID={h['id']}: '{h['nombre']}'")
    
    print("\n✅ Supabase limpiado")


if __name__ == "__main__":
    fix_sqlite()
    fix_supabase()
    print("\n" + "="*60)
    print("✅ TODO LIMPIO. Ahora ejecuta: python sync_system.py --force")
    print("="*60)
