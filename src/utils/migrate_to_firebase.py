import firebase_admin
from firebase_admin import credentials, firestore
import sqlite3
import pandas as pd
import sys
import os
import time
from tqdm import tqdm
from datetime import datetime
import warnings

# Suppress pandas warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# Fix for Windows Unicode printing
if sys.platform == "win32" and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Ensure we can import from src if running as script
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

try:
    from src.models.data_manager import cargar_programa
except ImportError:
    print("⚠️ Warning: Could not import cargar_programa. Metadata will be missing.")
    def cargar_programa(solo_futuras=True): return pd.DataFrame()

def init_firebase():
    """Inicializa Firebase Admin SDK."""
    cred_path = 'serviceAccountKey.json'
    # Check root or current dir
    if not os.path.exists(cred_path) and os.path.exists(f'../../{cred_path}'):
        cred_path = f'../../{cred_path}'
        
    try:
        if not firebase_admin._apps:
            if os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
            else:
                cred = credentials.ApplicationDefault()
                firebase_admin.initialize_app(cred, {'projectId': 'pista-inteligente'})
        return firestore.client()
    except Exception as e:
        print(f"❌ Error Init Firebase: {e}")
        sys.exit(1)


def retry_with_backoff(func, max_retries=3, initial_delay=1.0):
    """Retry function with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            delay = initial_delay * (2 ** attempt)
            print(f"⚠️ Attempt {attempt + 1} failed: {e}")
            print(f"   Retrying in {delay:.1f}s...")
            time.sleep(delay)

def get_sqlite_data(db_path='data/db/hipica_data.db'):
    """Lee datos de SQLite y los une en un DataFrame maestro."""
    if not os.path.exists(db_path) and os.path.exists(f'../../{db_path}'):
        db_path = f'../../{db_path}'
        
    if not os.path.exists(db_path):
        print(f"❌ Error: No se encontró DB {db_path}")
        return pd.DataFrame(), pd.DataFrame() 
        
    conn = sqlite3.connect(db_path)
    
    # 1. Carreras + Participaciones (Historical) for legacy sync
    q = """
    SELECT 
        jor.fecha, h.nombre as hipodromo, car.id as carrera_id,
        car.distancia, car.pista, car.condicion,
        p.posicion, p.mandil, p.tiempo, p.peso_fs, p.dividendo,
        c.nombre as caballo, j.nombre as jinete
    FROM participaciones p
    JOIN carreras car ON p.carrera_id = car.id
    JOIN jornadas jor ON car.jornada_id = jor.id
    JOIN hipodromos h ON jor.hipodromo_id = h.id
    JOIN caballos c ON p.caballo_id = c.id
    JOIN jinetes j ON p.jinete_id = j.id
    """
    
    try:
        df = pd.read_sql(q, conn)
    except:
        df = pd.DataFrame()
    
    # 2. Predicciones Activas
    print("⏳ Leyendo predicciones activas (JSON)...")
    json_path = 'data/predicciones_activas.json'
    if not os.path.exists(json_path) and os.path.exists(f'../../{json_path}'):
        json_path = f'../../{json_path}'
        
    try:
        df_preds = pd.read_json(json_path)
    except:
        df_preds = pd.DataFrame()
        
    conn.close()
    return df, df_preds

def migrate(incremental=True):
    """
    Migra datos a Firestore
    
    Args:
        incremental: Si True, solo migra carreras nuevas/modificadas
    """
    print("🚀 Iniciando Migración a Firestore (FULL CLOUD)...")
    print(f"   Modo: {'INCREMENTAL' if incremental else 'COMPLETO'}")
    
    db = init_firebase()
    df_hist, df_preds = get_sqlite_data()
    
    # ==========================================
    # 🌟 ENRICHMENT: JOIN WITH PROGRAM METADATA
    # ==========================================
    if not df_preds.empty:
        print("📥 Cargando metadatos visuales del Programa...")
        
        # Determine strict DB path for cargar_programa logic fallback
        # cargar_programa uses 'data/db/hipica_data.db' default
        
        df_program = cargar_programa(solo_futuras=True)
        
        if not df_program.empty:
            # Normalize columns
            try:
                col_carrera = 'carrera' if 'carrera' in df_preds.columns else 'nro_carrera'
                df_preds['carrera_int'] = df_preds[col_carrera].fillna(0).astype(int)
                df_preds['numero_int'] = df_preds['numero'].fillna(0).astype(int)
                
                df_program['nro_carrera_int'] = df_program['nro_carrera'].fillna(0).astype(int)
                df_program['numero_int'] = df_program['numero'].fillna(0).astype(int)
                
                print("🔗 Fusionando Predicciones + Metadatos...")
                
                # Merge
                df_enriched = pd.merge(
                    df_preds, 
                    df_program[['fecha', 'hipodromo', 'nro_carrera_int', 'numero_int', 'jinete', 'hora', 'distancia', 'caballo']],
                    left_on=['fecha', 'hipodromo', 'carrera_int', 'numero_int'],
                    right_on=['fecha', 'hipodromo', 'nro_carrera_int', 'numero_int'],
                    how='left',
                    suffixes=('', '_meta')
                )
                
                # Fill Missing Metadata
                df_enriched['jinete'] = df_enriched['jinete'].fillna('N/A')
                df_enriched['hora'] = df_enriched['hora'].fillna('00:00')
                df_enriched['distancia'] = df_enriched['distancia'].fillna(0).astype(int)
                
                # If cached prediction had no horse name or weird one, use program name
                if 'caballo_meta' in df_enriched.columns:
                     df_enriched['caballo'] = df_enriched['caballo_meta'].fillna(df_enriched['caballo'])
                
                # Detectar cambios para migración incremental
                if incremental:
                    print("🔍 Verificando cambios desde última migración...")
                    df_enriched['data_hash'] = df_enriched.apply(
                        lambda r: hash((r['fecha'], r['hipodromo'], r['carrera_int'], 
                                       r['numero_int'], r['probabilidad'])), axis=1
                    )
                
                df_preds = df_enriched
                print(f"✅ Predicciones enriquecidas: {len(df_preds)} registros.")
                
            except Exception as e:
                print(f"⚠️ Error en fusión de metadatos: {e}")
                print("   -> Subiendo predicciones sin enriquecer.")

    # ==========================================
    # 🧹 SANITIZACIÓN
    # ==========================================
    print("🧹 Sanitizando datos...")
    
    if not df_preds.empty:
        # Integers
        cols_int = ['numero', 'carrera', 'distancia']
        for col in cols_int:
            if col in df_preds.columns:
                df_preds[col] = pd.to_numeric(df_preds[col], errors='coerce').fillna(0).astype(int)
        
        # Floats
        if 'probabilidad' in df_preds.columns:
            df_preds['probabilidad'] = pd.to_numeric(df_preds['probabilidad'], errors='coerce').fillna(0.0)
            
        # Strings
        cols_str = ['jinete', 'hora', 'hipodromo', 'caballo']
        for col in cols_str:
            if col in df_preds.columns:
                df_preds[col] = df_preds[col].fillna("Unknown").astype(str)

    # --- MIGRAR PREDICCIONES (FUTURO) ---
    if not df_preds.empty:
        print("☁️ Subiendo Predicciones ENRIQUECIDAS...")
        
        # Ensure key
        col_carrera = 'carrera' if 'carrera' in df_preds.columns else 'nro_carrera'
        df_preds['key'] = df_preds['fecha'].astype(str) + "_" + df_preds['hipodromo'] + "_" + df_preds[col_carrera].astype(str)
        
        grouped_preds = df_preds.groupby('key')
        
        batch = db.batch()
        batch_count = 0
        total_uploaded = 0
        total_skipped = 0
        batch_size = 450  # Slightly below 500 limit for safety
        
        for key, group in tqdm(grouped_preds, desc="Predicciones"):
            first = group.iloc[0]
            
            doc_id = key.replace(" ", "_").replace("/", "-")
            
            # Ensure Date Format YYYY-MM-DD
            fecha_val = first['fecha']
            if isinstance(fecha_val, pd.Timestamp):
                fecha_str = fecha_val.strftime('%Y-%m-%d')
            else:
                # If string like "2025-12-29 00:00:00", clean it
                fecha_str = str(fecha_val).split(' ')[0]

            # RACE HEADER
            pred_data = {
                'fecha': fecha_str,
                'hipodromo': str(first['hipodromo']),
                'carrera': int(first['carrera']) if 'carrera' in first else int(first['nro_carrera']),
                'hora': str(first.get('hora', '00:00')),
                'distancia': int(first.get('distancia', 0)),
                'updated_at': firestore.SERVER_TIMESTAMP,
                'detalles': []
            }
            
            detalles = []
            for _, row in group.iterrows():
                # FIX: Filtro estricto de números inválidos
                num = int(row['numero'])
                if num <= 0: continue
                
                detalles.append({
                    'caballo': str(row['caballo']),
                    'numero': num,
                    'jinete': str(row.get('jinete', 'N/A')),
                    'probabilidad': float(row['probabilidad'])
                })
            
            # Ordenar explícitamente por probabilidad (Mayor a Menor) para la vista correcta
            detalles.sort(key=lambda x: x['probabilidad'], reverse=True)
            
            # Validar que probabilidades sean razonables (suma ~100%)
            total_prob = sum(d['probabilidad'] for d in detalles)
            if total_prob < 80 or total_prob > 120:
                print(f"⚠️ Warning: Race {key} probabilidad total = {total_prob:.1f}%")
            
            pred_data['detalles'] = detalles
            
            # Verificar si hay cambios (incremental)
            if incremental:
                ref = db.collection('predicciones').document(doc_id)
                try:
                    existing = ref.get()
                    if existing.exists:
                        # Comparar detalles
                        existing_data = existing.to_dict()
                        if existing_data.get('detalles') == detalles:
                            total_skipped += 1
                            continue  # Sin cambios, skip
                except Exception:
                    pass  # Si falla lectura, migrar de todos modos
            
            # Upload con retry
            ref = db.collection('predicciones').document(doc_id)
            
            def upload_batch():
                batch.set(ref, pred_data)
            
            try:
                retry_with_backoff(upload_batch)
            except Exception as e:
                print(f"❌ Error subiendo {doc_id}: {e}")
                continue
            
            batch_count += 1
            if batch_count >= batch_size:
                try:
                    retry_with_backoff(lambda: batch.commit())
                    print(f"   ✅ Batch {total_uploaded // batch_size + 1} committed ({batch_count} docs)")
                except Exception as e:
                    print(f"❌ Error committing batch: {e}")
                batch = db.batch()
                batch_count = 0
            
            total_uploaded += 1
                
        if batch_count > 0:
            try:
                retry_with_backoff(lambda: batch.commit())
                print(f"   ✅ Final batch committed ({batch_count} docs)")
            except Exception as e:
                print(f"❌ Error committing final batch: {e}")
            
        print(f"✅ Migradas {total_uploaded} carreras completas a Firestore.")
        if incremental and total_skipped > 0:
            print(f"   ⏭️ Skipped {total_skipped} carreras sin cambios (incremental)")
    else:
        print("⚠️ No hay predicciones para migrar.")

    print("\n🎉 MIGRACIÓN FULL CLOUD COMPLETADA.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Migrate to Firestore')
    parser.add_argument('--full', action='store_true', help='Full migration (no incremental)')
    args = parser.parse_args()
    
    migrate(incremental=not args.full)
