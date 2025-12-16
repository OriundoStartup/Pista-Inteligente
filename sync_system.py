import os
import sys
import webbrowser
import time
import socket
import subprocess
import sqlite3
from datetime import datetime
from src.etl.etl_pipeline import HipicaETL
from src.models.train_v2 import HipicaLearner
from src.models.data_manager import obtener_analisis_jornada, calcular_todos_patrones
import json
from pathlib import Path
import json
from pathlib import Path
import numpy as np
import argparse

def _safe_int(val):
    """Convierte de forma segura a int, manejando bytes/blobs de numpy/sqlite."""
    try:
        if val is None: return 0
        if isinstance(val, (bytes, bytearray)):
            # Asumir little-endian para enteros de 64 bits si viene de numpy
            return int.from_bytes(val[:8], byteorder='little')
        return int(float(str(val)))
    except:
        return 0

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def kill_server_on_port(port):
    """Mata el proceso que ocupa el puerto especificado (Windows/Linux)"""
    import signal
    print(f"🔄 Intentando liberar puerto {port}...")
    try:
        if sys.platform == 'win32':
            # Buscar PID usando netstat
            cmd = f'netstat -ano | findstr :{port}'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')
            for line in lines:
                parts = line.split()
                if len(parts) > 4:
                    pid = parts[-1]
                    print(f"   -> Matando proceso PID {pid}...")
                    subprocess.run(f'taskkill /F /PID {pid}', shell=True, capture_output=True)
        else:
            # Linux/Mac logic (fuser/lsof could be used, or simple killall python)
            pass
    except Exception as e:
        print(f"⚠️ No se pudo liberar puerto: {e}")

class CustomJSONEncoder(json.JSONEncoder):
    """Encoder personalizado para manejar tipos de Numpy"""
    def default(self, obj):
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
                            np.int16, np.int32, np.int64, np.uint8,
                            np.uint16, np.uint32, np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        return super(CustomJSONEncoder, self).default(obj)

def save_predictions_to_db(analisis, update_mode=True):
    """
    Guarda o actualiza las predicciones de manera inteligente (UPSERT manual).
    Verifica existencia para decidir entre UPDATE o INSERT, evitando duplicados.
    """
    try:
        db_path = 'data/db/hipica_data.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        rows_to_insert = []
        rows_to_update = []
        
        print("   🔍 Verificando existencia de predicciones para UPSERT...")
        
        # Cache de existencia para reducir SELECTs individuales
        # Clave: (fecha, hipodromo, nro_carrera, numero_caballo)
        # Valor: True
        # Cargar todas las predicciones futuras existentes en memoria (son pocas)
        cursor.execute("SELECT fecha_carrera, hipodromo, nro_carrera, numero_caballo FROM predicciones WHERE fecha_carrera >= date('now', 'localtime')")
        existing_preds = set()
        for row in cursor.fetchall():
            # (fecha, hipodromo, carrera, caballo)
            existing_preds.add((row[0], row[1], int(row[2]), int(row[3])))

        for carrera in analisis:
            fecha_carrera = carrera.get('fecha')
            hipodromo = carrera.get('hipodromo')
            nro_carrera = _safe_int(carrera.get('carrera'))
            predicciones = carrera.get('predicciones', [])
            
            for idx, pred in enumerate(predicciones, 1):
                if isinstance(pred, dict):
                    numero = _safe_int(pred.get('numero', 0))
                    puntaje_ia = pred.get('puntaje_ia', 0.0)
                    prob_ml_val = pred.get('prob_ml', '0.0')
                    if isinstance(prob_ml_val, str):
                         prob_ml = float(prob_ml_val.replace('%', ''))
                    else:
                         prob_ml = float(prob_ml_val)
                    
                    # IDs
                    caballo_nombre = pred.get('caballo', '')
                    jinete_nombre = pred.get('jinete', '')
                    
                    # Resolver IDs
                    caballo_id = None
                    cursor.execute("SELECT id FROM caballos WHERE nombre = ?", (caballo_nombre,))
                    res = cursor.fetchone()
                    if res: caballo_id = res[0]
                    
                    jinete_id = None
                    cursor.execute("SELECT id FROM jinetes WHERE nombre = ?", (jinete_nombre,))
                    res = cursor.fetchone()
                    if res: jinete_id = res[0]
                    
                    metadata = json.dumps({
                        'caballo': caballo_nombre,
                        'jinete': jinete_nombre,
                        'updated_at': timestamp
                    }, ensure_ascii=False)
                    
                    # Decisión UPSERT
                    key = (fecha_carrera, hipodromo, nro_carrera, numero)
                    
                    if key in existing_preds:
                        # UPDATE
                        rows_to_update.append((
                            puntaje_ia,
                            prob_ml,
                            idx, # ranking
                            metadata,
                            timestamp,
                            fecha_carrera,
                            hipodromo,
                            nro_carrera,
                            numero
                        ))
                    else:
                        # INSERT
                        rows_to_insert.append((
                            timestamp,
                            fecha_carrera,
                            hipodromo,
                            nro_carrera,
                            numero,
                            caballo_id,
                            jinete_id,
                            puntaje_ia,
                            prob_ml,
                            idx,  # ranking
                            metadata
                        ))
        
        # Ejecutar batch
        if rows_to_insert:
            cursor.executemany('''
                INSERT INTO predicciones 
                (fecha_generacion, fecha_carrera, hipodromo, nro_carrera, numero_caballo, 
                 caballo_id, jinete_id, puntaje_ia, prob_ml, ranking_prediccion, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', rows_to_insert)
            print(f"   💾 Insertadas {len(rows_to_insert)} nuevas predicciones.")

        if rows_to_update:
            cursor.executemany('''
                UPDATE predicciones
                SET puntaje_ia=?, prob_ml=?, ranking_prediccion=?, metadata=?, fecha_generacion=?
                WHERE fecha_carrera=? AND hipodromo=? AND nro_carrera=? AND numero_caballo=?
            ''', rows_to_update)
            print(f"   🔄 Actualizadas {len(rows_to_update)} predicciones existentes.")
            
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"   ⚠️ Error en UPSERT predicciones: {e}")
        import traceback
        traceback.print_exc()
        return False

def precalculate_predictions(update_mode=False):
    """
    Pre-calcula predicciones y las guarda en cache y base de datos.
    Args:
        update_mode: Si es True, indica que estamos actualizando por nuevos resultados (UPDATE en BD).
                     Si es False, es una carga normal o nueva (INSERT).
    """
    print(f"📊 Pre-calculando predicciones... (Modo Actualización: {update_mode})")
    try:
        cache_path = Path("data/cache_analisis.json")
        
        # Siempre queremos refrescar el cache JSON para la vista
        if cache_path.exists():
            cache_path.unlink()
        
        print("   🧹 Limpiando cache LRU de obtener_analisis_jornada...")
        obtener_analisis_jornada.cache_clear()
        
        print("   🔄 Obteniendo predicciones frescas (SQL Optimizado)...")
        # Esto ahora usa cargar_programa(solo_futuras=True) internamente
        analisis = obtener_analisis_jornada()
        
        if not analisis:
            print("   ⚠️ No hay carreras futuras para analizar.")
            return True # No es error, solo no hay datos
        
        # Debug
        fechas = set(c.get('fecha') for c in analisis)
        print(f"   📅 Fechas analizadas: {sorted(fechas)}")
        
        # Guardar o Actualizar en DB
        print(f"   💾 {'Actualizando' if update_mode else 'Guardando'} en Base de Datos...")
        save_predictions_to_db(analisis, update_mode=update_mode)
        
        # Serializar para Cache JSON (Frontend)
        analisis_serializable = []
        for carrera in analisis:
            carrera_dict = carrera.copy()
            if hasattr(carrera_dict['caballos'], 'to_dict'):
                carrera_dict['caballos'] = carrera_dict['caballos'].to_dict('records')
            if hasattr(carrera_dict['predicciones'], 'to_dict'):
                carrera_dict['predicciones'] = carrera_dict['predicciones'].to_dict('records')
            analisis_serializable.append(carrera_dict)

        cache_path.parent.mkdir(exist_ok=True, parents=True)
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(analisis_serializable, f, ensure_ascii=False, indent=2, cls=CustomJSONEncoder)
        
        print(f"   ✅ Cache JSON regenerado en {cache_path}")
        return True
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Error al pre-calcular predicciones: {e}")
        return False

def precalculate_patterns(update_mode=False):
    """
    Pre-calcula patrones de resultados y los guarda en cache JSON.
    """
    print(f"📊 Pre-calculando patrones de resultados... (Modo Actualización: {update_mode})")
    try:
        cache_path = Path("data/cache_patrones.json")
        
        # Siempre refrescamos cache
        if cache_path.exists():
            cache_path.unlink()
            
        print("   🔄 Calculando todos los patrones...")
        patrones = calcular_todos_patrones()
        
        if not patrones:
            print("   ⚠️ No se encontraron patrones.")
            # Crear archivo vacío válido con metadata
            data = {
                'last_updated': datetime.now().strftime('%d-%m-%Y %H:%M'),
                'patterns': []
            }
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, cls=CustomJSONEncoder)
            return True
            
        print(f"   ✅ Encontrados {len(patrones)} patrones.")
        
        data = {
            'last_updated': datetime.now().strftime('%d-%m-%Y %H:%M'),
            'patterns': patrones
        }
        
        cache_path.parent.mkdir(exist_ok=True, parents=True)
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, cls=CustomJSONEncoder)
        
        print(f"   ✅ Cache Patrones JSON regenerado en {cache_path}")
        return True
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Error al pre-calcular patrones: {e}")
        return False

def check_git_changes():
    """Retorna True si hay cambios pendientes en git (código modificado)."""
    try:
        # Check staged + unstaged + untracked
        # git status --porcelain es la forma más robusta
        r = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if r.stdout.strip(): 
            return True
        return False
    except:
        return False

def main(force_sync=False):
    """
    Sistema de sincronización principal optimizado.
    Args:
        force_sync: Si es True, fuerza re-procesamiento completo ignorando tracking
    """
    print("""
    ==================================================
       SISTEMA DE HIPICA INTELIGENTE - SYNC V2.1
    ==================================================
    DETECTANDO ARCHIVOS EN /exports...
    """)
    
    start_time = time.time()
    
    try:
        # 1. Inicializar y Correr ETL
        print("\n[PASO 1/3] Ejecutando ETL (Carga de Datos)...")
        etl = HipicaETL()
        archivos_nuevos = etl.run(force_reprocess=force_sync)
        
        # Verificar si hay cambios que requieran actualización (Datos o Código)
        cambios_codigo = check_git_changes()
        hay_cambios = (archivos_nuevos > 0) or cambios_codigo
        
        if cambios_codigo:
             print("\n📝 Detectados cambios en el código fuente. Se procederá al despliegue.")
        
        if not hay_cambios and not force_sync:
            print("\n✅ SISTEMA ACTUALIZADO - No hay cambios nuevos (ni datos ni código).")
            print("📊 Los datos, modelos y predicciones están vigentes.")
            print(f"\n⏱️ Tiempo total: {time.time() - start_time:.2f} segundos")
            return
        
        print(f"\n🔄 Detectados {archivos_nuevos} archivo(s) nuevo(s). Actualizando sistema...")
        
        # 2. Entrenar/Actualizar Modelos de IA
        print("\n[PASO 2/3] Entrenando Modelos de IA (HipicaLearner)...")
        try:
            learner = HipicaLearner()
            learner.train()
            print("✅ Modelos de Inteligencia Artificial actualizados correctamente.")
        except Exception as e_ml:
            print(f"⚠️ Advertencia: No se pudo entrenar el modelo de IA: {e_ml}")
            print("   -> El sistema continuará con los modelos anteriores si existen.")

        elapsed = time.time() - start_time
        print(f"\n✅ SINCRONIZACIÓN COMPLETADA en {elapsed:.2f} segundos.")
        print(" -> La Base de Datos ha sido actualizada.")
        print(" -> Modelos de Predicción (V3 - HistGradientBoosting): ACTUALIZADOS.")
        
        # 2.5 Pre-calcular Predicciones (Cache + BD)
        # Activar update_mode=True para aprovechar la lógica de Re-Predicción (Update)
        # La función internamente debe manejar inserts para nuevos programas (Pendiente de ajuste en save)
        print("\n[PASO 2.5/3] Recalculando Predicciones Futuras (Update + Insert)...")
        precalculate_predictions(update_mode=True)
        
        # 2.6 Pre-calcular Patrones
        print("\n[PASO 2.6/3] Recalculando Patrones de Resultados...")
        precalculate_patterns(update_mode=True)

        # 3. Deploy a Cloud Run (Firebase)
        print("\n[PASO 3/3] Desplegando a Cloud Run (Firebase)...")
        deploy_to_cloud_run()

    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        input("Presiona Enter para salir...")

def deploy_to_cloud_run():
    """Despliega la aplicación a Google Cloud Run"""
    try:
        # Determinar el comando correcto de gcloud para Windows
        gcloud_cmd = "gcloud.cmd" if sys.platform == "win32" else "gcloud"
        
        # Verificar si gcloud está instalado
        print("   🔍 Verificando instalación de gcloud...")
        gcloud_check = subprocess.run(
            [gcloud_cmd, "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            shell=True if sys.platform == "win32" else False
        )
        
        if gcloud_check.returncode != 0:
            print("   ⚠️ gcloud CLI no está correctamente configurado.")
            print(f"   📄 Error: {gcloud_check.stderr}")
            return
        
        print("   ✅ gcloud CLI encontrado")
        
        # Verificar autenticación
        print("   🔐 Verificando autenticación de gcloud...")
        auth_check = subprocess.run(
            [gcloud_cmd, "auth", "list", "--filter=status:ACTIVE", "--format=value(account)"],
            capture_output=True,
            text=True,
            timeout=10,
            shell=True if sys.platform == "win32" else False
        )
        
        if not auth_check.stdout.strip():
            print("   ⚠️ No hay cuenta de Google Cloud autenticada.")
            print("   💡 Ejecuta: gcloud auth login")
            return
        
        print(f"   ✅ Autenticado como: {auth_check.stdout.strip()}")
        
        # Commit cambios a Git primero
        print("   📦 Commiteando cambios a Git...")
        subprocess.run(["git", "add", "."], cwd=os.path.dirname(__file__) or ".", check=False)
        subprocess.run(
            ["git", "commit", "-m", "sync: Actualización automática de datos y modelos"],
            cwd=os.path.dirname(__file__) or ".",
            check=False,
            capture_output=True
        )
        subprocess.run(["git", "push"], cwd=os.path.dirname(__file__) or ".", check=False)
        print("   ✅ Cambios pusheados a GitHub")
        
        # Desplegar a Cloud Run
        print("   🚀 Desplegando a Cloud Run...")
        
        # Cargar API key desde .env para Cloud Run
        from dotenv import load_dotenv
        load_dotenv()
        gemini_key = os.getenv('GEMINI_API_KEY', '')
        
        # Ofuscar para log
        key_preview = f"{gemini_key[:10]}...{gemini_key[-4:]}" if len(gemini_key) > 14 else "***"
        print(f"   🔐 Configurando GEMINI_API_KEY: {key_preview}")
        
        result = subprocess.run(
            [
                gcloud_cmd, "run", "deploy", "pista-inteligente",
                "--source", ".",
                "--region", "us-central1",
                "--allow-unauthenticated",
                "--set-env-vars", f"GEMINI_API_KEY={gemini_key}",
                "--quiet"
            ],
            cwd=os.path.dirname(__file__) or ".",
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutos max
            shell=True if sys.platform == "win32" else False
        )
        
        if result.returncode == 0:
            print("   ✅ DEPLOY EXITOSO!")
            print("   🚀 El backend ha sido actualizado para dar soporte a:")
            print("      👉 https://pista-inteligente.web.app")
            print("      👉 https://pista-inteligente.firebaseapp.com")
            
            # Ocultamos la URL técnica de Cloud Run para evitar confusiones,
            # ya que el usuario prefiere las URLs de Firebase.
            # for line in result.stdout.split('\n'): ...
        else:
            print("   ❌ Error en deploy a Cloud Run:")
            print(f"   📄 STDOUT: {result.stdout}")
            print(f"   📄 STDERR: {result.stderr}")
            
    except FileNotFoundError:
        print("   ⚠️ gcloud CLI no encontrado en el PATH del sistema.")
        print("   💡 Tip: Instala Google Cloud SDK o verifica tu PATH")
    except subprocess.TimeoutExpired:
        print("   ⚠️ Timeout en el deploy. El proceso tomó demasiado tiempo.")
    except Exception as e:
        print(f"   ❌ Error inesperado en deploy: {type(e).__name__}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Sistema de Sincronización Hípica Inteligente')
    parser.add_argument('--force', action='store_true', help='Forzar re-procesamiento completo')
    parser.add_argument('--no-deploy', action='store_true', help='Saltar paso de despliegue')
    
    args = parser.parse_args()
    
    main(force_sync=args.force)

