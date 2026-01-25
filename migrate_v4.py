"""
Script de migración v4: Solo migra las participaciones que tienen FKs válidas.
Enfoque pragmático: En lugar de limpiar todo y reinsertar, 
insertamos solo las participaciones que tienen carrera_id dentro del rango
de carreras existentes en Supabase (1-83).
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

def main():
    print("=" * 60)
    print("   MIGRACIÓN PRAGMÁTICA DE PARTICIPACIONES (v4)")
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
    
    # 1. Obtener carreras existentes en Supabase
    print("\n📊 Obteniendo IDs de carreras existentes en Supabase...")
    carreras_res = supabase.table('carreras').select('id').execute()
    carrera_ids_supabase = set([c['id'] for c in carreras_res.data])
    print(f"   Carreras en Supabase: {len(carrera_ids_supabase)}")
    print(f"   Rango IDs: {min(carrera_ids_supabase)} - {max(carrera_ids_supabase)}")
    
    # 2. Obtener IDs de caballos y jinetes en Supabase
    caballos_res = supabase.table('caballos').select('id').execute()
    caballo_ids_supabase = set([c['id'] for c in caballos_res.data])
    print(f"   Caballos en Supabase: {len(caballo_ids_supabase)}")
    
    jinetes_res = supabase.table('jinetes').select('id').execute()
    jinete_ids_supabase = set([j['id'] for j in jinetes_res.data])
    print(f"   Jinetes en Supabase: {len(jinete_ids_supabase)}")
    
    # 3. Leer participaciones de SQLite
    print("\n📥 Leyendo participaciones de SQLite...")
    df = pd.read_sql("SELECT * FROM participaciones", conn)
    print(f"   Total participaciones en SQLite: {len(df)}")
    
    # 4. Filtrar participaciones que tienen FKs válidas
    print("\n🔍 Filtrando participaciones con FKs válidas...")
    
    df_valid = df[
        (df['carrera_id'].isin(carrera_ids_supabase)) &
        (df['caballo_id'].isin(caballo_ids_supabase)) &
        (df['jinete_id'].isin(jinete_ids_supabase))
    ]
    
    print(f"   Participaciones válidas: {len(df_valid)}")
    print(f"   Participaciones excluidas (FKs inválidas): {len(df) - len(df_valid)}")
    
    if df_valid.empty:
        print("⚠️ No hay participaciones con FKs válidas.")
        
        # Mostrar diagnóstico de qué falta
        print("\n📋 DIAGNÓSTICO:")
        sample = df.head(10)
        for _, row in sample.iterrows():
            c_ok = "✅" if row['carrera_id'] in carrera_ids_supabase else "❌"
            j_ok = "✅" if row['jinete_id'] in jinete_ids_supabase else "❌"
            cab_ok = "✅" if row['caballo_id'] in caballo_ids_supabase else "❌"
            print(f"   carrera:{row['carrera_id']}{c_ok} jinete:{row['jinete_id']}{j_ok} caballo:{row['caballo_id']}{cab_ok}")
        
        conn.close()
        return
    
    # 5. Preparar datos
    # Renombrar columnas
    if 'mandil' in df_valid.columns:
        df_valid = df_valid.rename(columns={'mandil': 'numero_mandil'})
    if 'peso_fs' in df_valid.columns:
        df_valid = df_valid.rename(columns={'peso_fs': 'peso_jinete'})
    
    # Limpiar dividendo
    if 'dividendo' in df_valid.columns:
        df_valid['dividendo'] = df_valid['dividendo'].astype(str).str.replace(',', '.', regex=False)
        df_valid['dividendo'] = pd.to_numeric(df_valid['dividendo'], errors='coerce')
    
    # Columnas permitidas (sin 'id')
    allowed_cols = ['carrera_id', 'caballo_id', 'jinete_id', 'posicion', 
                   'numero_mandil', 'peso_jinete', 'dividendo']
    
    existing = [c for c in allowed_cols if c in df_valid.columns]
    df_valid = df_valid[existing].copy()
    
    # Asegurar tipos enteros
    for col in ['carrera_id', 'caballo_id', 'jinete_id', 'posicion', 'numero_mandil']:
        if col in df_valid.columns:
            df_valid[col] = pd.to_numeric(df_valid[col], errors='coerce').fillna(0).astype(int)
    
    print(f"   Columnas: {existing}")
    
    records = clean_for_json(df_valid)
    
    # 6. Limpiar participaciones existentes
    print("\n🧹 Limpiando participaciones existentes en Supabase...")
    try:
        result = supabase.table('participaciones').select('id').limit(10000).execute()
        if result.data:
            ids = [r['id'] for r in result.data]
            for i in range(0, len(ids), 100):
                batch_ids = ids[i:i+100]
                supabase.table('participaciones').delete().in_('id', batch_ids).execute()
        print(f"   Eliminados: {len(result.data) if result.data else 0}")
    except Exception as e:
        print(f"   ⚠️ {str(e)[:80]}")
    
    # 7. Insertar participaciones
    print("\n📤 Insertando participaciones en Supabase...")
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
    
    print(f"\n✅ Resultado: {success} ok, {errors} errores")
    
    conn.close()
    
    # Verificación final
    print("\n" + "=" * 60)
    print("   VERIFICACIÓN FINAL")
    print("=" * 60)
    
    count = supabase.table('participaciones').select('*', count='exact', head=True).execute()
    print(f"   Participaciones en Supabase: {count.count}")
    
    # Test de la consulta del frontend
    print("\n🧪 Probando consulta del frontend...")
    try:
        data = supabase.from_('participaciones').select(
            'posicion, jinetes(nombre)'
        ).eq('posicion', 1).limit(10).execute()
        
        if data.data:
            print("   ✅ Ganadores encontrados:")
            for r in data.data[:5]:
                jinete = r.get('jinetes', {})
                nombre = jinete.get('nombre', 'N/A') if jinete else 'N/A'
                print(f"      - {nombre}")
        else:
            print("   ⚠️ No se encontraron ganadores")
    except Exception as e:
        print(f"   ❌ Error en consulta: {e}")

if __name__ == "__main__":
    main()
