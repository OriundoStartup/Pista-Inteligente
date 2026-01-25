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
            
        # Select only columns that match Supabase target (filtering others)
        # We need to know Supabase schema, but generally we rely on mapping.
        # If no mapping, we assume names match.
        
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
            
            # Clean NaN/Null values (Postgres doesn't like NaN)
            clean_batch = []
            for r in batch:
                clean_r = {k: (None if pd.isna(v) else v) for k, v in r.items()}
                
                # SPECIAL FIXES
                # Boolean conversion? Date string?
                clean_batch.append(clean_r)

            # Upsert
            # Note: Supabase-py 'upsert' might need checking if it respects ID
            res = client.upsert(supabase_table, clean_batch, on_conflict=on_conflict)
            
            # Simple Insert if upsert fails? No, Upsert is safer for re-runs.
            
        print(f"   ✅ Migration of {table_name} completed.")
        
    except Exception as e:
        print(f"   ❌ Error migrating {table_name}: {e}")

def run_migration():
    print("🏁 Starting Full Migration to Supabase...")
    
    # 1. Hipodromos - Special handling to preserve SQLite IDs
    # We need to ensure the IDs in Supabase match SQLite exactly for foreign key references
    print("\n🚀 Migrating table: hipodromos -> hipodromos...")
    conn = get_sqlite_conn()
    if conn:
        df = pd.read_sql("SELECT id, nombre FROM hipodromos", conn)
        conn.close()
        
        if not df.empty:
            print(f"   Items to migrate: {len(df)}")
            records = df.to_dict('records')
            client = SupabaseManager()
            
            # First delete existing hipodromos to avoid conflicts
            # This is safe because we'll re-insert all data
            try:
                # Delete all existing records
                client.get_client().table('hipodromos').delete().neq('id', -1).execute()
                print("   🗑️ Cleared existing hipodromos")
            except Exception as e:
                print(f"   ⚠️ Could not clear hipodromos: {e}")
            
            # Now insert with exact SQLite IDs
            try:
                # Clean records
                clean_records = [{k: (None if pd.isna(v) else v) for k, v in r.items()} for r in records]
                client.get_client().table('hipodromos').insert(clean_records).execute()
                print("   ✅ Hipodromos migrated with preserved IDs")
            except Exception as e:
                print(f"   ❌ Error inserting hipodromos: {e}")
    
    # 2. Caballos (only columns that exist in Supabase)
    migrate_table('caballos', 'caballos', on_conflict='id', columns=['id', 'nombre'])
    
    # 3. Jinetes
    migrate_table('jinetes', 'jinetes', on_conflict='id')
    
    # 4. Jornadas
    # SQLite: jornadas(id, hipodromo_id, fecha)
    migrate_table('jornadas', 'jornadas', on_conflict='id')
    
    # 5. Carreras
    # SQLite: carreras(id, jornada_id, numero, ...)
    # Mapping: numero -> numero, distancia -> distancia
    migrate_table('carreras', 'carreras', on_conflict='id')
    
    # 6. Participaciones
    # SQLite: participaciones(id, carrera_id, caballo_id, jinete_id, posicion, ...)
    # Supabase: participaciones(..., dividendo type changes?)
    # En SQLite 'dividendo' a veces es string con coma.
    # Necesitamos limpiar 'dividendo' a float puntor.
    
    print("\n🚀 Migrating Participaciones (with cleaning)...")
    conn = get_sqlite_conn()
    if conn:
        df = pd.read_sql("SELECT * FROM participaciones", conn)
        conn.close()
        
        if not df.empty:
            # Cleaning
            if 'dividendo' in df.columns:
                df['dividendo'] = df['dividendo'].astype(str).str.replace(',', '.', regex=False)
                df['dividendo'] = pd.to_numeric(df['dividendo'], errors='coerce')
                
            if 'peso_fs' in df.columns:
                df = df.rename(columns={'peso_fs': 'peso_jinete'})
            
            # Rename 'mandil' to 'numero_mandil'
            df = df.rename(columns={'mandil': 'numero_mandil'})
            
            # Batch Upload
            records = df.to_dict('records')
            client = SupabaseManager()
            
            batch_size = 500
            print(f"   Items: {len(records)}")
            for i in tqdm(range(0, len(records), batch_size)):
                batch = records[i:i+batch_size]
                clean_batch = [{k: (None if pd.isna(v) else v) for k, v in r.items()} for r in batch]
                
                # ID Handling: SQLite has ID? Yes. 
                # Our Supabase schema has UUID default, but we can store ID if we change type or just ignore old ID and let new one?
                # IF WE IGNORE ID, WE LOSE REFERENCE?
                # SQLite participaciones.id is likely Integer.
                # Supabase participaciones.id is UUID.
                # WE CANNOT INSERT INTEGER INTO UUID.
                # DECISION: Drop the 'id' from SQLite and let Supabase generate new UUIDs.
                # Participaciones usually are not referenced by foreign keys (they are leaves).
                # So it is safe to drop 'id'.
                for r in clean_batch:
                    if 'id' in r: del r['id']
                    
                client.insert('participaciones', clean_batch)
                
            print("   ✅ Participaciones migrated.")

if __name__ == "__main__":
    run_migration()
