"""
Script para migrar participaciones con limpieza robusta de tipos.
"""
import sqlite3
import os
import sys
import pandas as pd
from tqdm import tqdm

sys.path.append(os.path.dirname(__file__))
from src.utils.supabase_client import SupabaseManager

DB_PATH = 'data/db/hipica_data.db'

def migrate_participaciones():
    print("🚀 Migración de Participaciones con limpieza de tipos...")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ DB no encontrada: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    
    # Leer participaciones
    df = pd.read_sql("SELECT * FROM participaciones", conn)
    conn.close()
    
    print(f"📦 Participaciones a migrar: {len(df)}")
    print(f"📋 Columnas: {list(df.columns)}")
    
    if df.empty:
        print("⚠️ No hay participaciones")
        return
    
    # === LIMPIEZA DE DATOS ===
    
    # 1. Dividendo: string con coma -> float
    if 'dividendo' in df.columns:
        df['dividendo'] = df['dividendo'].astype(str).str.replace(',', '.', regex=False)
        df['dividendo'] = pd.to_numeric(df['dividendo'], errors='coerce')
    
    # 2. Columnas que deben ser INTEGER (no float)
    int_columns = ['carrera_id', 'caballo_id', 'jinete_id', 'posicion', 'numero_mandil']
    
    for col in int_columns:
        if col in df.columns:
            # Convertir a entero, manejando NaN
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = df[col].fillna(0).astype(int)
            
    # 3. Rename mandil -> numero_mandil si existe
    if 'mandil' in df.columns and 'numero_mandil' not in df.columns:
        df = df.rename(columns={'mandil': 'numero_mandil'})
    
    # 4. Rename peso_fs -> peso_jinete si existe
    if 'peso_fs' in df.columns:
        df = df.rename(columns={'peso_fs': 'peso_jinete'})
    
    # 5. Eliminar columna 'id' (Supabase genera UUID)
    if 'id' in df.columns:
        df = df.drop(columns=['id'])
    
    print(f"📋 Columnas finales: {list(df.columns)}")
    
    # Convertir a lista de dicts
    records = df.to_dict('records')
    
    # Limpiar valores NaN
    clean_records = []
    for r in records:
        clean_r = {}
        for k, v in r.items():
            if pd.isna(v):
                clean_r[k] = None
            elif isinstance(v, float) and v == int(v):
                clean_r[k] = int(v)  # 93.0 -> 93
            else:
                clean_r[k] = v
        clean_records.append(clean_r)
    
    # Subir a Supabase en batches
    client = SupabaseManager()
    supabase = client.get_client()
    
    if not supabase:
        print("❌ No se pudo conectar a Supabase")
        return
    
    batch_size = 500
    success_count = 0
    error_count = 0
    
    for i in tqdm(range(0, len(clean_records), batch_size)):
        batch = clean_records[i:i+batch_size]
        
        try:
            result = supabase.table('participaciones').insert(batch).execute()
            success_count += len(batch)
        except Exception as e:
            print(f"\n❌ Error en batch {i//batch_size + 1}: {e}")
            error_count += len(batch)
            # Intentar insertar uno por uno para identificar el registro problemático
            if error_count < 50:  # Limitar errores detallados
                for j, record in enumerate(batch[:5]):
                    try:
                        supabase.table('participaciones').insert(record).execute()
                    except Exception as e2:
                        print(f"   Record {i+j} error: {e2}")
                        print(f"   Data: {record}")
    
    print(f"\n✅ Migración completada: {success_count} exitosos, {error_count} errores")

if __name__ == "__main__":
    migrate_participaciones()
