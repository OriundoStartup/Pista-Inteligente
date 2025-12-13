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
from src.models.data_manager import obtener_analisis_jornada
import json
from pathlib import Path
import numpy as np

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

def save_predictions_to_db(analisis):
    """Guarda las predicciones en la base de datos para historial permanente."""
    try:
        db_path = 'data/db/hipica_data.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        predicciones_batch = []
        
        for carrera in analisis:
            fecha_carrera = carrera.get('fecha')
            hipodromo = carrera.get('hipodromo')
            nro_carrera = carrera.get('carrera')
            predicciones = carrera.get('predicciones', [])
            
            for idx, pred in enumerate(predicciones, 1):
                # Extraer datos de la predicción
                if isinstance(pred, dict):
                    numero = pred.get('numero', 0)
                    puntaje_ia = pred.get('puntaje_ia', 0.0)
                    prob_ml = float(str(pred.get('prob_ml', '0.0')).replace('%', ''))
                    
                    # Buscar IDs de caballo y jinete
                    caballo_nombre = pred.get('caballo', '')
                    jinete_nombre = pred.get('jinete', '')
                    
                    caballo_id = None
                    jinete_id = None
                    
                    if caballo_nombre:
                        cursor.execute("SELECT id FROM caballos WHERE nombre = ?", (caballo_nombre,))
                        result = cursor.fetchone()
                        if result:
                            caballo_id = result[0]
                    
                    if jinete_nombre:
                        cursor.execute("SELECT id FROM jinetes WHERE nombre = ?", (jinete_nombre,))
                        result = cursor.fetchone()
                        if result:
                            jinete_id = result[0]
                    
                    # Crear metadata JSON con información adicional
                    metadata = json.dumps({
                        'caballo': caballo_nombre,
                        'jinete': jinete_nombre
                    }, ensure_ascii=False)
                    
                    predicciones_batch.append((
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
        
        if predicciones_batch:
            cursor.executemany('''
                INSERT INTO predicciones 
                (fecha_generacion, fecha_carrera, hipodromo, nro_carrera, numero_caballo, 
                 caballo_id, jinete_id, puntaje_ia, prob_ml, ranking_prediccion, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', predicciones_batch)
            conn.commit()
            print(f"   💾 {len(predicciones_batch)} predicciones guardadas en base de datos")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"   ⚠️ Error guardando predicciones en BD: {e}")
        import traceback
        traceback.print_exc()
        return False

def precalculate_predictions():
    """Pre-calcula predicciones y las guarda en cache y base de datos"""
    print("📊 Pre-calculando predicciones...")
    try:
        cache_path = Path("data/cache_analisis.json")
        
        # CRITICAL: Eliminar el archivo de cache JSON para forzar recálculo completo
        if cache_path.exists():
            print(f"   🗑️  Eliminando cache antiguo: {cache_path}")
            cache_path.unlink()
            print("   ✅ Cache antiguo eliminado")
        
        # Limpiar cache de memoria LRU para asegurar datos frescos
        print("   🧹 Limpiando cache LRU de obtener_analisis_jornada...")
        obtener_analisis_jornada.cache_clear()
        print("   ✅ Cache LRU limpiado")
        
        # Ahora obtener_analisis_jornada se verá forzado a recalcular desde la BD
        print("   🔄 Recalculando predicciones desde base de datos...")
        analisis = obtener_analisis_jornada()
        
        # Debug: mostrar fechas procesadas
        fechas = set(c.get('fecha') for c in analisis)
        print(f"   📅 Fechas procesadas: {sorted(fechas)}")
        print(f"   🏁 Total de carreras: {len(analisis)}")
        
        # Guardar en base de datos (NUEVO)
        print("   💾 Guardando predicciones en base de datos...")
        save_predictions_to_db(analisis)
        
        # Convertir DataFrames a dicts si es necesario
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
        
        print(f"   ✅ Cache JSON guardado en {cache_path}")
        return True
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ Error al pre-calcular predicciones: {e}")
        return False

def main():
    print("""
    ==================================================
       🏇 SISTEMA DE HÍPICA INTELIGENTE - SYNC V2.1 🏇
    ==================================================
    DETECTANDO ARCHIVOS EN /exports...
    """)
    
    start_time = time.time()
    
    try:
        # 1. Inicializar y Correr ETL
        print("\n[PASO 1/3] Ejecutando ETL (Carga de Datos)...")
        etl = HipicaETL()
        etl.run()
        
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
        
        # 2.5 Pre-calcular Predicciones (Cache)
        print("\n[PASO 2.5/3] Pre-calculando Predicciones para Web...")
        precalculate_predictions()

        # 3. Deploy a Cloud Run (Firebase)
        print("\n[PASO 3/3] Desplegando a Cloud Run (Firebase)...")
        deploy_to_cloud_run()

    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
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
            print("   ✅ DEPLOY EXITOSO a Cloud Run!")
            # Extraer URL del output
            for line in result.stdout.split('\n'):
                if 'https://' in line:
                    print(f"   🌐 URL: {line.strip()}")
                    break
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
    main()

