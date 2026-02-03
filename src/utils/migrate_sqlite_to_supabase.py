import sqlite3
import os
import sys
import pandas as pd
from tqdm import tqdm

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.utils.supabase_client import SupabaseManager

DB_PATH = 'data/db/hipica_data.db'

def get_sqlite_conn():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return None
    return sqlite3.connect(DB_PATH)

def migrate_table(table_name, supabase_table, mapping=None, on_conflict=None, columns=None):
    """
    Reads a table from SQLite and upserts to Supabase.
    mapping: Dict {sqlite_col: supabase_col}
    on_conflict: Column name to use for conflict resolution (upsert)
    columns: List of columns to include (if None, includes all)
    """
    print(f"\n🚀 Migrating table: {table_name} -> {supabase_table}...")
    
    conn = get_sqlite_conn()
    if not conn: return
    
    try:
        # Read from SQLite
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        conn.close()
        
        if df.empty:
            print(f"   ⚠️ Table {table_name} is empty.")
            return

        print(f"   Items to migrate: {len(df)}")
        
        # Rename columns
        if mapping:
            df = df.rename(columns=mapping)
        
        # Filter to only specified columns if provided
        if columns:
            df = df[[col for col in columns if col in df.columns]]
        
        # CRITICAL: Convert integer columns to native Python int
        # This prevents issues with numpy types causing "40.0" errors
        for col in df.columns:
            if col == 'id' or col.endswith('_id'):
                df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
            
        # Convert df to list of dicts
        records = df.to_dict('records')
        
        # Batch insert
        client = SupabaseManager()
        if not client.get_client():
            print("   ❌ Supabase client not available.")
            return

        batch_size = 1000
        for i in tqdm(range(0, len(records), batch_size)):
            batch = records[i:i+batch_size]
            
            # Clean NaN/Null values and convert types
            clean_batch = []
            for r in batch:
                clean_r = {}
                for k, v in r.items():
                    if pd.isna(v):
                        clean_r[k] = None
                    elif k == 'id' or k.endswith('_id'):
                        # Convert to native Python int
                        try:
                            clean_r[k] = int(v)
                        except (ValueError, TypeError):
                            clean_r[k] = None
                    else:
                        clean_r[k] = v
                clean_batch.append(clean_r)

            # Upsert with on_conflict to handle existing records
            res = client.upsert(supabase_table, clean_batch, on_conflict=on_conflict)
            
        print(f"   ✅ Migration of {table_name} completed.")
        
    except Exception as e:
        print(f"   ❌ Error migrating {table_name}: {e}")

def run_migration():
    print("🏁 Starting Full Migration to Supabase...")
    
    client = SupabaseManager()
    if not client.get_client():
        print("❌ Supabase client not available.")
        return
    
    # =========================================================
    # NOTA: NO limpiamos tablas - usamos upsert para preservar IDs
    # La limpieza causaba que Supabase auto-genere nuevos IDs,
    # rompiendo las foreign keys de participaciones
    # =========================================================
    
    # 1. Hipodromos - Usar UPSERT para evitar errores de clave duplicada
    print("\n🚀 Migrating table: hipodromos -> hipodromos...")
    conn = get_sqlite_conn()
    if conn:
        df = pd.read_sql("SELECT id, nombre FROM hipodromos", conn)
        conn.close()
        
        if not df.empty:
            print(f"   Items to migrate: {len(df)}")
            records = df.to_dict('records')
            
            # Usar UPSERT en lugar de delete+insert
            # Filter out existing hipodromos by name to avoid Unique Key violations
            try:
                # Get existing names from Supabase
                res = client.get_client().table('hipodromos').select('nombre').execute()
                existing_names = {r['nombre'] for r in res.data} if res.data else set()
                
                # Filter records
                clean_records = []
                for r in records:
                    if r.get('nombre') not in existing_names:
                        clean_records.append({k: (None if pd.isna(v) else v) for k, v in r.items()})
                    else:
                        print(f"   ℹ️ Skipping existing hipodromo: {r.get('nombre')}")
                
                if clean_records:
                    print(f"   New hipodromos to sync: {len(clean_records)}")
                    client.get_client().table('hipodromos').upsert(clean_records, on_conflict='id').execute()
                    print("   ✅ New hipodromos inserted.")
                else:
                    print("   ✅ No new hipodromos to sync.")
                    
            except Exception as e:
                print(f"   ❌ Error checking/upserting hipodromos: {e}")
    
    # 2. Caballos (only columns that exist in Supabase)
    migrate_table('caballos', 'caballos', on_conflict='id', columns=['id', 'nombre'])
    
    # 3. Jinetes
    migrate_table('jinetes', 'jinetes', on_conflict='id')
    
    # 3.5 Studs
    migrate_table('studs', 'studs', on_conflict='id')
    
    # ============================================================
    # 4. Jornadas - Use natural key (hipodromo_nombre, fecha) for mapping
    # ============================================================
    print("\n🚀 Migrating Jornadas (with hipodromo mapping)...")
    conn = get_sqlite_conn()
    if conn:
        # Get jornadas with hipodromo nombre for natural key
        sqlite_jornadas = pd.read_sql("""
            SELECT j.id, j.hipodromo_id, j.fecha, h.nombre as hipodromo_nombre
            FROM jornadas j
            JOIN hipodromos h ON j.hipodromo_id = h.id
        """, conn)
        
        # Get hipodromo mapping: nombre -> Supabase ID
        supabase_hip = client.get_client().table('hipodromos').select('id, nombre').execute()
        hip_name_to_id = {r['nombre']: r['id'] for r in supabase_hip.data} if supabase_hip.data else {}
        
        if sqlite_jornadas.empty:
            print("   ⚠️ No jornadas in SQLite")
        else:
            # Map hipodromo_id to Supabase IDs
            records = []
            for _, row in sqlite_jornadas.iterrows():
                sup_hip_id = hip_name_to_id.get(row['hipodromo_nombre'])
                if sup_hip_id:
                    records.append({
                        'hipodromo_id': sup_hip_id,
                        'fecha': str(row['fecha'])
                    })
            
            print(f"   Items: {len(records)}")
            if records:
                # Upsert using natural key
                try:
                    client.get_client().table('jornadas').upsert(
                        records, on_conflict='hipodromo_id,fecha'
                    ).execute()
                    print(f"   ✅ Jornadas migrated: {len(records)}")
                except Exception as e:
                    print(f"   ❌ Error: {e}")
        conn.close()
    
    # ============================================================
    # 5. Carreras - Use natural key (jornada via hipodromo+fecha, numero)
    # ============================================================
    print("\n🚀 Migrating Carreras (with jornada mapping)...")
    conn = get_sqlite_conn()
    if conn:
        # Get carreras with full natural key
        sqlite_carreras = pd.read_sql("""
            SELECT c.*, j.fecha, h.nombre as hipodromo_nombre
            FROM carreras c
            JOIN jornadas j ON c.jornada_id = j.id
            JOIN hipodromos h ON j.hipodromo_id = h.id
        """, conn)
        conn.close()
        
        # Get current jornadas from Supabase for mapping
        sup_jornadas = client.get_client().table('jornadas').select(
            'id, fecha, hipodromos(nombre)'
        ).execute()
        
        # Build jornada lookup: (hipodromo_nombre, fecha) -> jornada_id
        jornada_lookup = {}
        if sup_jornadas.data:
            for j in sup_jornadas.data:
                if j.get('hipodromos'):
                    key = (j['hipodromos']['nombre'], j['fecha'])
                    jornada_lookup[key] = j['id']
        
        # Get existing carreras from Supabase to avoid duplicates
        existing_carreras = client.get_client().table('carreras').select(
            'jornada_id, numero'
        ).execute()
        existing_set = {(r['jornada_id'], r['numero']) for r in existing_carreras.data} if existing_carreras.data else set()
        print(f"   Existing carreras in Supabase: {len(existing_set)}")
        
        if sqlite_carreras.empty:
            print("   ⚠️ No carreras in SQLite")
        else:
            # Map jornada_id to Supabase IDs and filter out existing
            records = []
            for _, row in sqlite_carreras.iterrows():
                key = (row['hipodromo_nombre'], str(row['fecha']))
                sup_jornada_id = jornada_lookup.get(key)
                if sup_jornada_id:
                    carrera_key = (sup_jornada_id, int(row['numero']))
                    if carrera_key not in existing_set:  # Only insert new
                        record = {
                            'jornada_id': sup_jornada_id,
                            'numero': int(row['numero']),
                        }
                        # Add optional fields if they exist and are valid
                        if 'distancia' in row and pd.notna(row['distancia']):
                            try:
                                record['distancia'] = int(row['distancia'])
                            except (ValueError, TypeError):
                                pass
                        # Validate hora - should contain ':' for time format
                        if 'hora' in row and pd.notna(row['hora']):
                            hora_str = str(row['hora'])
                            if ':' in hora_str:  # Valid time like "15:30"
                                record['hora'] = hora_str
                        # Other string fields
                        for col in ['pista', 'tipo', 'grado', 'condicion']:
                            if col in row and pd.notna(row[col]):
                                record[col] = str(row[col])
                        records.append(record)
            
            print(f"   New carreras to insert: {len(records)}")
            if records:
                # Insert in batches
                batch_size = 100
                inserted = 0
                for i in range(0, len(records), batch_size):
                    batch = records[i:i+batch_size]
                    try:
                        client.get_client().table('carreras').insert(batch).execute()
                        inserted += len(batch)
                    except Exception as e:
                        print(f"   ⚠️ Error batch {i//batch_size}: {str(e)[:80]}")
                print(f"   ✅ Carreras migrated: {inserted} new records")
    
    # 6. Participaciones - CRITICAL: Map using cascading natural keys
    print("\n🚀 Migrating Participaciones (with full ID mapping)...")
    conn = get_sqlite_conn()
    if conn:
        # ============================================================
        # Step 1: Build COMPLETE cascading ID mapping using natural keys
        # hipodromo_nombre -> jornada(fecha) -> carrera(numero)
        # ============================================================
        print("   📋 Building cascading ID mappings...")
        
        # Get ALL data from SQLite with natural keys
        sqlite_data = pd.read_sql("""
            SELECT 
                c.id as sqlite_carrera_id,
                c.numero as carrera_numero,
                j.fecha,
                h.nombre as hipodromo_nombre
            FROM carreras c
            JOIN jornadas j ON c.jornada_id = j.id
            JOIN hipodromos h ON j.hipodromo_id = h.id
        """, conn)
        
        # Get ALL data from Supabase with natural keys
        sup_carreras = client.get_client().table('carreras').select(
            'id, numero, jornadas(fecha, hipodromos(nombre))'
        ).execute()
        
        # Build Supabase lookup: (hipodromo_nombre, fecha, numero) -> supabase_carrera_id
        supabase_lookup = {}
        if sup_carreras.data:
            for r in sup_carreras.data:
                if r.get('jornadas') and r['jornadas'].get('hipodromos'):
                    key = (
                        r['jornadas']['hipodromos']['nombre'],
                        r['jornadas']['fecha'],
                        r['numero']
                    )
                    supabase_lookup[key] = r['id']
        
        # Create SQLite ID -> Supabase ID mapping
        carrera_id_map = {}
        for _, row in sqlite_data.iterrows():
            key = (row['hipodromo_nombre'], str(row['fecha']), int(row['carrera_numero']))
            if key in supabase_lookup:
                carrera_id_map[int(row['sqlite_carrera_id'])] = supabase_lookup[key]
        
        print(f"   ✅ Mapped {len(carrera_id_map)} carreras (SQLite->Supabase)")
        
        if len(carrera_id_map) == 0:
            print("   ⚠️ No carreras mapped - check if Supabase has carreras with jornadas/hipodromos")
            conn.close()
            return
        
        # ============================================================
        # Step 2: Get participaciones and apply mapping
        # ============================================================
        df = pd.read_sql("SELECT * FROM participaciones", conn)
        conn.close()
        
        if not df.empty:
            # Map carrera_id to Supabase IDs
            df['carrera_id'] = df['carrera_id'].apply(
                lambda x: carrera_id_map.get(int(x)) if pd.notna(x) and int(x) in carrera_id_map else None
            )
            
            # Remove rows where carrera_id couldn't be mapped
            original_count = len(df)
            df = df.dropna(subset=['carrera_id'])
            dropped = original_count - len(df)
            if dropped > 0:
                print(f"   ⚠️ Dropped {dropped} rows with unmapped carrera_id")
            
            if df.empty:
                print("   ❌ No participaciones after mapping - all carrera_ids were unmapped")
                return
            
            # Cleaning
            if 'dividendo' in df.columns:
                df['dividendo'] = df['dividendo'].astype(str).str.replace(',', '.', regex=False)
                df['dividendo'] = pd.to_numeric(df['dividendo'], errors='coerce')
                
            if 'peso_fs' in df.columns:
                df = df.rename(columns={'peso_fs': 'peso_jinete'})
            
            df = df.rename(columns={'mandil': 'numero_mandil'})
            
            # Convert integer columns
            int_columns = ['carrera_id', 'caballo_id', 'jinete_id', 'stud_id', 'posicion', 'numero_mandil']
            for col in int_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
            
            # Batch Upload
            records = df.to_dict('records')
            
            batch_size = 500
            success_count = 0
            print(f"   Items to upload: {len(records)}")
            for i in tqdm(range(0, len(records), batch_size)):
                batch = records[i:i+batch_size]
                clean_batch = []
                for r in batch:
                    clean_r = {}
                    for k, v in r.items():
                        if pd.isna(v):
                            clean_r[k] = None
                        else:
                            try:
                                clean_r[k] = int(v) if k in int_columns else v
                            except (ValueError, TypeError):
                                clean_r[k] = v if k not in int_columns else None
                    # Drop SQLite id
                    if 'id' in clean_r: del clean_r['id']
                    clean_batch.append(clean_r)
                
                try:
                    client.get_client().table('participaciones').upsert(
                        clean_batch, 
                        on_conflict='carrera_id,caballo_id'
                    ).execute()
                    success_count += len(clean_batch)
                except Exception as e:
                    print(f"   ⚠️ Error batch {i//batch_size}: {str(e)[:80]}")
                
            print(f"   ✅ Participaciones migrated: {success_count} records")

if __name__ == "__main__":
    run_migration()
