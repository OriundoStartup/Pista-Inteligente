"""
Script de migración LIMPIA: Elimina datos existentes y reinserta desde cero.
Esto asegura que los IDs coincidan entre SQLite y Supabase.
"""
import sqlite3
import os
import sys
import pandas as pd
from tqdm import tqdm
import time

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

def delete_all(supabase, table_name):
    """Elimina todos los registros de una tabla."""
    try:
        # Para tablas con UUID, usamos otro approach
        if table_name == 'participaciones':
            # Obtener todos los IDs y eliminar
            result = supabase.table(table_name).select('id').limit(10000).execute()
            if result.data:
                ids = [r['id'] for r in result.data]
                for i in range(0, len(ids), 100):
                    batch_ids = ids[i:i+100]
                    supabase.table(table_name).delete().in_('id', batch_ids).execute()
            print(f"   🗑️ {table_name} limpiada ({len(result.data) if result.data else 0} registros)")
        else:
            # Para tablas con ID entero
            supabase.table(table_name).delete().gt('id', -1).execute()
            print(f"   🗑️ {table_name} limpiada")
    except Exception as e:
        print(f"   ⚠️ {table_name}: {str(e)[:80]}")


def migrate_table_clean(conn, supabase, table_name, select_cols=None, rename_cols=None, exclude_cols=None):
    """Migra tabla con limpieza previa y columnas filtradas."""
    print(f"\n🚀 Migrando {table_name}...")
    
    # Construir query SELECT
    if select_cols:
        query = f"SELECT {', '.join(select_cols)} FROM {table_name}"
    else:
        query = f"SELECT * FROM {table_name}"
    
    df = pd.read_sql(query, conn)
    print(f"   📦 Registros: {len(df)}")
    
    if df.empty:
        return 0
    
    # Renombrar columnas
    if rename_cols:
        df = df.rename(columns=rename_cols)
    
    # Excluir columnas
    if exclude_cols:
        df = df.drop(columns=[c for c in exclude_cols if c in df.columns], errors='ignore')
    
    print(f"   📋 Columnas: {list(df.columns)}")
    
    records = clean_for_json(df)
    
    # Insertar (no upsert, porque ya limpiamos)
    batch_size = 500
    success = 0
    
    for i in tqdm(range(0, len(records), batch_size), desc=f"   {table_name}"):
        batch = records[i:i+batch_size]
        try:
            supabase.table(table_name).insert(batch).execute()
            success += len(batch)
        except Exception as e:
            print(f"\n   ❌ Error: {str(e)[:150]}")
    
    print(f"   ✅ Insertados: {success}/{len(records)}")
    return success

def main():
    print("=" * 60)
    print("   MIGRACIÓN LIMPIA SQLite -> Supabase (v3)")
    print("   ¡ATENCIÓN! Esto eliminará datos existentes.")
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
    
    # Paso 1: Limpiar todas las tablas en orden inverso de dependencias
    print("\n" + "=" * 40)
    print("   PASO 1: LIMPIANDO TABLAS")
    print("=" * 40)
    
    for table in ['participaciones', 'carreras', 'jornadas', 'jinetes', 'caballos', 'hipodromos']:
        delete_all(supabase, table)
        time.sleep(0.5)  # Pequeña pausa para API
    
    # Paso 2: Migrar en orden de dependencias
    print("\n" + "=" * 40)
    print("   PASO 2: MIGRANDO DATOS")
    print("=" * 40)
    
    # Hipódromos (solo id, nombre)
    migrate_table_clean(conn, supabase, 'hipodromos', 
                       select_cols=['id', 'nombre'])
    
    # Caballos (solo id, nombre)
    migrate_table_clean(conn, supabase, 'caballos',
                       select_cols=['id', 'nombre'])
    
    # Jinetes (solo id, nombre)
    migrate_table_clean(conn, supabase, 'jinetes',
                       select_cols=['id', 'nombre'])
    
    # Jornadas
    migrate_table_clean(conn, supabase, 'jornadas',
                       select_cols=['id', 'hipodromo_id', 'fecha'])
    
    # Carreras (solo columnas que existen)
    migrate_table_clean(conn, supabase, 'carreras',
                       select_cols=['id', 'jornada_id', 'numero', 'hora', 'distancia'])
    
    # Participaciones - tratamiento especial
    print("\n🚀 Migrando participaciones...")
    
    df = pd.read_sql("SELECT * FROM participaciones", conn)
    print(f"   📦 Registros: {len(df)}")
    
    if not df.empty:
        # Renombrar columnas
        rename_map = {
            'mandil': 'numero_mandil',
            'peso_fs': 'peso_jinete'
        }
        df = df.rename(columns=rename_map)
        
        # Limpiar dividendo
        if 'dividendo' in df.columns:
            df['dividendo'] = df['dividendo'].astype(str).str.replace(',', '.', regex=False)
            df['dividendo'] = pd.to_numeric(df['dividendo'], errors='coerce')
        
        # Columnas permitidas (sin 'id' de SQLite)
        allowed_cols = ['carrera_id', 'caballo_id', 'jinete_id', 'posicion', 
                       'numero_mandil', 'peso_jinete', 'dividendo', 'stud_id', 'haras_id', 'odds']
        
        existing = [c for c in allowed_cols if c in df.columns]
        df = df[existing]
        print(f"   📋 Columnas: {existing}")
        
        # Asegurar tipos enteros
        for col in ['carrera_id', 'caballo_id', 'jinete_id', 'posicion', 'numero_mandil']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
        records = clean_for_json(df)
        
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
                if errors <= 5:
                    print(f"\n   ❌ Error: {str(e)[:200]}")
        
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
