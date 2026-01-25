"""
Script de migración corregido que solo usa columnas que existen en Supabase.
Problema identificado: SQLite tiene columnas adicionales que no existen en Supabase.
"""
import sqlite3
import os
import sys
import pandas as pd
from tqdm import tqdm

sys.path.append(os.path.dirname(__file__))
from src.utils.supabase_client import SupabaseManager

DB_PATH = 'data/db/hipica_data.db'

# Columnas que existen en cada tabla de Supabase (basado en esquema conocido)
SUPABASE_COLUMNS = {
    'hipodromos': ['id', 'nombre'],
    'caballos': ['id', 'nombre'],  # Sin ano_nacimiento ni otros campos extra
    'jinetes': ['id', 'nombre'],  # Solo id y nombre
    'jornadas': ['id', 'hipodromo_id', 'fecha'],
    'carreras': ['id', 'jornada_id', 'numero', 'hora', 'distancia', 'pista', 'handicap', 'premio', 'descripcion'],
    'participaciones': [
        'carrera_id', 'caballo_id', 'jinete_id', 'posicion', 'numero_mandil',
        'peso_jinete', 'dividendo', 'stud_id', 'haras_id', 'odds'
    ]  # Sin 'id' porque Supabase usa UUID
}

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

def migrate_table(conn, supabase, table_name, allowed_cols=None):
    """Migra una tabla, filtrando solo columnas permitidas."""
    print(f"\n🚀 Migrando {table_name}...")
    
    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    print(f"   📦 Registros en SQLite: {len(df)}")
    
    if df.empty:
        return 0
    
    # Filtrar solo columnas que existen en Supabase
    if allowed_cols:
        # Manejar renombres
        if 'mandil' in df.columns and 'numero_mandil' in allowed_cols:
            df = df.rename(columns={'mandil': 'numero_mandil'})
        if 'peso_fs' in df.columns and 'peso_jinete' in allowed_cols:
            df = df.rename(columns={'peso_fs': 'peso_jinete'})
            
        existing_cols = [c for c in allowed_cols if c in df.columns]
        df = df[existing_cols]
        print(f"   📋 Columnas usadas: {existing_cols}")
    
    records = clean_for_json(df)
    
    batch_size = 500
    success = 0
    
    for i in tqdm(range(0, len(records), batch_size), desc=f"   {table_name}"):
        batch = records[i:i+batch_size]
        try:
            supabase.table(table_name).upsert(batch).execute()
            success += len(batch)
        except Exception as e:
            print(f"\n   ❌ Error: {str(e)[:100]}")
    
    print(f"   ✅ Migrados: {success}/{len(records)}")
    return success

def main():
    print("=" * 60)
    print("   MIGRACIÓN COMPLETA SQLite -> Supabase (v2)")
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
    
    # Migrar tablas en orden de dependencias
    migrate_table(conn, supabase, 'hipodromos', SUPABASE_COLUMNS['hipodromos'])
    migrate_table(conn, supabase, 'caballos', SUPABASE_COLUMNS['caballos'])
    migrate_table(conn, supabase, 'jinetes', SUPABASE_COLUMNS['jinetes'])
    migrate_table(conn, supabase, 'jornadas', SUPABASE_COLUMNS['jornadas'])
    migrate_table(conn, supabase, 'carreras', SUPABASE_COLUMNS['carreras'])
    
    # Participaciones: requiere tratamiento especial
    print("\n🚀 Migrando participaciones...")
    
    df = pd.read_sql("SELECT * FROM participaciones", conn)
    print(f"   📦 Registros en SQLite: {len(df)}")
    
    if not df.empty:
        # Renombrar columnas
        if 'mandil' in df.columns:
            df = df.rename(columns={'mandil': 'numero_mandil'})
        if 'peso_fs' in df.columns:
            df = df.rename(columns={'peso_fs': 'peso_jinete'})
        
        # Limpiar dividendo
        if 'dividendo' in df.columns:
            df['dividendo'] = df['dividendo'].astype(str).str.replace(',', '.', regex=False)
            df['dividendo'] = pd.to_numeric(df['dividendo'], errors='coerce')
        
        # Filtrar columnas
        allowed = SUPABASE_COLUMNS['participaciones']
        existing_cols = [c for c in allowed if c in df.columns]
        df = df[existing_cols]
        print(f"   📋 Columnas usadas: {existing_cols}")
        
        # Asegurar tipos enteros
        for col in ['carrera_id', 'caballo_id', 'jinete_id', 'posicion', 'numero_mandil']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
        records = clean_for_json(df)
        
        # Limpiar participaciones existentes
        print("   🧹 Limpiando participaciones existentes en Supabase...")
        try:
            supabase.table('participaciones').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        except Exception as e:
            print(f"   ⚠️ Limpieza fallida (puede estar vacía): {str(e)[:50]}")
        
        # Insertar en batches
        batch_size = 300
        success = 0
        errors = 0
        
        for i in tqdm(range(0, len(records), batch_size), desc="   participaciones"):
            batch = records[i:i+batch_size]
            try:
                supabase.table('participaciones').insert(batch).execute()
                success += len(batch)
            except Exception as e:
                errors += len(batch)
                if errors <= 10:
                    print(f"\n   ❌ Error batch: {str(e)[:150]}")
        
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
            print(f"   {table}: Error - {str(e)[:50]}")

if __name__ == "__main__":
    main()
