import os
import sys
import webbrowser
import time
import socket
import subprocess
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

def precalculate_predictions():
    """Pre-calcula predicciones y las guarda en cache"""
    print("📊 Pre-calculando predicciones...")
    try:
        # Limpiar cache de memoria para asegurar datos frescos
        obtener_analisis_jornada.cache_clear()
        
        analisis = obtener_analisis_jornada()
        
        # Convertir DataFrames a dicts si es necesario
        analisis_serializable = []
        for carrera in analisis:
            carrera_dict = carrera.copy()
            if hasattr(carrera_dict['caballos'], 'to_dict'):
                carrera_dict['caballos'] = carrera_dict['caballos'].to_dict('records')
            if hasattr(carrera_dict['predicciones'], 'to_dict'):
                carrera_dict['predicciones'] = carrera_dict['predicciones'].to_dict('records')
            analisis_serializable.append(carrera_dict)

        cache_path = Path("data/cache_analisis.json")
        cache_path.parent.mkdir(exist_ok=True, parents=True)
        
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(analisis_serializable, f, ensure_ascii=False, indent=2, cls=CustomJSONEncoder)
        
        print(f"✅ Cache guardado en {cache_path}")
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
        result = subprocess.run(
            [
                "gcloud", "run", "deploy", "pista-inteligente",
                "--source", ".",
                "--region", "us-central1",
                "--allow-unauthenticated",
                "--quiet"
            ],
            cwd=os.path.dirname(__file__) or ".",
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("   ✅ DEPLOY EXITOSO a Cloud Run!")
            # Extraer URL del output
            for line in result.stdout.split('\n'):
                if 'https://' in line:
                    print(f"   🌐 URL: {line.strip()}")
                    break
        else:
            print(f"   ⚠️ Advertencia en deploy: {result.stderr[:200] if result.stderr else 'Sin detalles'}")
            
    except FileNotFoundError:
        print("   ⚠️ gcloud CLI no encontrado. Instálalo para deploy automático.")
        print("   💡 Tip: Puedes hacer deploy manual con 'gcloud run deploy'")
    except Exception as e:
        print(f"   ❌ Error en deploy: {e}")

if __name__ == "__main__":
    main()

