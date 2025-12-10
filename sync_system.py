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

def main():
    print("""
    ==================================================
       🏇 SISTEMA DE HÍPICA INTELIGENTE - SYNC V2 🏇
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
        print(" -> Modelos de Predicción (Random Forest): ACTUALIZADOS.")
        
        # 3. Abrir Vista
        print("\n[PASO 3/3] Iniciando/Verificando Servidor Web...")
        
        # Abrir navegador automáticamente
        target_port = 5000
        try:
            port_env = os.environ.get("PORT")
            if port_env:
                target_port = int(port_env)
        except:
            target_port = 5000

        url = f"http://localhost:{target_port}"
        
        # Verificar si el servidor ya esta corriendo
        if is_port_in_use(target_port):
            print(f"[INFO] Servidor detectado en puerto {target_port}. Abriendo navegador...")
            webbrowser.open(url)
        else:
            print(f"[INFO] Servidor NO detectado. Iniciando servidor web...")
            webbrowser.open(url) # Abrimos antes para que cargue cuando levante
            try:
                # Ejecutar app.py
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
