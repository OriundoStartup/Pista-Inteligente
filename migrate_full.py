"""
Script completo de migración SQLite -> Supabase con manejo robusto de IDs.
Problema: Supabase tiene IDs diferentos o incompletos.
Solución: Usar UPSERT con ID explícito para mantener consistencia de FKs.
"""
import sqlite3
import os
import sys
import pandas as pd
from tqdm import tqdm

sys.path.append(os.path.dirname(__file__))
from src.utils.supabase_client import SupabaseManager

DB_PATH = 'data/db/hipica_data.db'

def clean_for_json(df):
    """Limpia DataFrame para inserción en Supabase."""
    records = df.to_dict('records')
    clean_records = []
    for r in records:
        clean_r = {}
        for k, v in r.items():
            if pd.isna(v):
                clean_r[k] = None
            elif isinstance(v, float) and v == int(v):
                clean_r[k] = int(v)
            else:
                clean_r[k] = v
        clean_records.append(clean_r)
    return clean_records

def migrate_table(conn, supabase, table_name, rename_cols=None):
    """Migra una tabla con upsert por ID."""
    print(f"\n🚀 Migrando {table_name}...")
    
    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    print(f"   📦 Registros: {len(df)}")
    
    if df.empty:
        print(f"   ⚠️ Tabla vacía")
        return 0
    
    # Renombrar columnas si es necesario
    if rename_cols:
        df = df.rename(columns=rename_cols)
    
    records = clean_for_json(df)
    
    # Batch upsert
    batch_size = 500
    success = 0
    
    for i in tqdm(range(0, len(records), batch_size)):
        batch = records[i:i+batch_size]
        try:
            result = supabase.table(table_name).upsert(batch).execute()
            success += len(batch)
        except Exception as e:
            print(f"\n   ❌ Error: {e}")
            # Intentar uno por uno
            for record in batch:
                try:
                    supabase.table(table_name).upsert(record).execute()
                    success += 1
                except Exception as e2:
                    print(f"   ❌ Record error: {record.get('id', '?')}: {str(e2)[:100]}")
    
    print(f"   ✅ Migrados: {success}/{len(records)}")
    return success

def main():
    print("=" * 60)
    print("   MIGRACIÓN COMPLETA SQLite -> Supabase")
    print("=" * 60)
    
    if not os.path.exists(DB_PATH):
        print(f"❌ DB no encontrada: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    
    client = SupabaseManager()
    supabase = client.get_client()
    
    if not supabase:
        print("❌ No se pudo conectar a Supabase")
        conn.close()
        return
    
    # 1. Hipódromos (base)
    migrate_table(conn, supabase, 'hipodromos')
    
    # 2. Caballos (independiente)
    migrate_table(conn, supabase, 'caballos')
    
    # 3. Jinetes (independiente)  
    migrate_table(conn, supabase, 'jinetes')
    
    # 4. Jornadas (depende de hipodromos)
    migrate_table(conn, supabase, 'jornadas')
    
    # 5. Carreras (depende de jornadas)
    migrate_table(conn, supabase, 'carreras')
    
    # 6. Participaciones (depende de carreras, caballos, jinetes)
    print("\n🚀 Migrando participaciones (con limpieza especial)...")
    
    df = pd.read_sql("SELECT * FROM participaciones", conn)
    print(f"   📦 Registros: {len(df)}")
    
    if not df.empty:
        # Limpiar dividendo
        if 'dividendo' in df.columns:
            df['dividendo'] = df['dividendo'].astype(str).str.replace(',', '.', regex=False)
            df['dividendo'] = pd.to_numeric(df['dividendo'], errors='coerce')
        
        # Renombrar columnas
        if 'mandil' in df.columns:
            df = df.rename(columns={'mandil': 'numero_mandil'})
        if 'peso_fs' in df.columns:
            df = df.rename(columns={'peso_fs': 'peso_jinete'})
        
        # Asegurar que IDs sean enteros
        for col in ['carrera_id', 'caballo_id', 'jinete_id', 'posicion']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
        # Eliminar ID local (Supabase usa UUID)
        if 'id' in df.columns:
            df = df.drop(columns=['id'])
        
        records = clean_for_json(df)
        
        # Primero limpiar participaciones existentes (si hay duplicados)
        try:
            print("   🧹 Limpiando participaciones existentes...")
            # Usar delete segmentado
            supabase.table('participaciones').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        except Exception as e:
            print(f"   ⚠️ No se pudieron limpiar (puede que esté vacía): {e}")
        
        # Insertar por batches
        batch_size = 300
        success = 0
        errors = 0
        
        for i in tqdm(range(0, len(records), batch_size)):
            batch = records[i:i+batch_size]
            try:
                result = supabase.table('participaciones').insert(batch).execute()
                success += len(batch)
            except Exception as e:
                errors += len(batch)
                if errors <= 50:
                    print(f"\n   ❌ Batch error: {str(e)[:150]}")
        
        print(f"   ✅ Participaciones: {success} ok, {errors} errores")
    
    conn.close()
    
    # Verificación final
    print("\n" + "=" * 60)
    print("   VERIFICACIÓN FINAL")
    print("=" * 60)
    
    for table in ['hipodromos', 'caballos', 'jinetes', 'jornadas', 'carreras', 'participaciones']:
        try:
            count = supabase.table(table).select('*', count='exact', head=True).execute()
            print(f"   {table}: {count.count}")
        except Exception as e:
            print(f"   {table}: Error - {e}")

if __name__ == "__main__":
    main()
