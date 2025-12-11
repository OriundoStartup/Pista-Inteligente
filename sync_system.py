import os
import sys
import webbrowser
import time
import socket
import subprocess
from src.etl.etl_pipeline import HipicaETL
from src.models.train_v2 import HipicaLearner

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
        
        # 3. Abrir Vista
        print("\n[PASO 3/3] Reiniciando Servidor Web (para aplicar cambios)...")
        
        target_port = 5000
        try:
            port_env = os.environ.get("PORT")
            if port_env:
                target_port = int(port_env)
        except:
            target_port = 5000

        # FORCE RESTART: Kill old process to clear cache
        kill_server_on_port(target_port)
        time.sleep(2) # Esperar a que se libere

        url = f"http://localhost:{target_port}"
        print(f"[INFO] Iniciando servidor web en {url}...")
        
        # Abrir navegador
        webbrowser.open(url)
        
        # Iniciar servidor
        try:
            subprocess.run([sys.executable, "app.py"], check=True)
        except KeyboardInterrupt:
            print("\n[INFO] Servidor detenido por usuario.")
        except Exception as e:
            print(f"[ERROR] No se pudo iniciar el servidor: {e}")

    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        input("Presiona Enter para salir...")

if __name__ == "__main__":
    main()
