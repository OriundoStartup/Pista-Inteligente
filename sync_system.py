import os
import time
import sys
import argparse
import subprocess
from datetime import datetime

# --- FIX PARA WINDOWS/EMOJIS ---
# Fuerza la salida de la consola a UTF-8 para evitar UnicodeEncodeError
if sys.platform == "win32" and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# --- IMPORTACIONES DEL SISTEMA V2.0 ---
try:
    from src.etl.etl_pipeline import HipicaETL
    from src.models.train_v2 import HipicaLearner
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print("Asegúrate de ejecutar este script desde la raíz del proyecto (python sync_system.py)")
    sys.exit(1)

def main(force_sync=False):
    """
    SISTEMA DE HIPICA INTELIGENTE - SYNC V2.0 (LOCAL / CONTENEDOR)
    Orquestador principal: ETL -> Entrenamiento -> Inferencia
    """
    print("""
    ==================================================
       SISTEMA DE HIPICA INTELIGENTE - SYNC V2.0
       (MODO: LOCAL / CONTENEDOR)
    ==================================================
    """)
    
    start_time = time.time()
    
    try:
        # ---------------------------------------------------------
        # PASO 1: ETL (Cargar datos nuevos de la web)
        # ---------------------------------------------------------
        print("\n[PASO 1/3] Ejecutando ETL (Extracción de Datos)...")
        etl = HipicaETL()
        # force_reprocess permite bajar todo de nuevo si es necesario
        archivos_nuevos = etl.run(force_reprocess=force_sync)
        
        if archivos_nuevos == 0 and not force_sync:
            print("\n✅ No hay datos históricos nuevos.")
        else:
            print(f"\n✅ Se han procesado {archivos_nuevos} archivos nuevos.")

        # ---------------------------------------------------------
        # PASO 2: RE-ENTRENAMIENTO (Solo si hubo datos nuevos o se fuerza)
        # ---------------------------------------------------------
        # Si llegaron resultados nuevos, el modelo debe aprender de ellos.
        if archivos_nuevos > 0 or force_sync:
            print("\n[PASO 2/3] Entrenando Modelo 'Learning to Rank' (LGBM)...")
            try:
                learner = HipicaLearner()
                learner.train() # Genera lgbm_ranker_v1.pkl
                print("✅ Modelo re-entrenado exitosamente.")
            except Exception as e:
                print(f"⚠️ Error en entrenamiento: {e}")
                print(" -> Se usará la versión anterior del modelo.")
        else:
            print("\n[PASO 2/3] Saltando entrenamiento (Modelo vigente).")

        # ---------------------------------------------------------
        # PASO 3: INFERENCIA (Predicciones para mañana)
        # ---------------------------------------------------------
        # Siempre ejecutamos inferencia, porque puede haber programas nuevos para mañana
        print("\n[PASO 3/3] Ejecutando Pipeline de Inferencia...")
        
        # Ejecutamos como subproceso para garantizar limpieza de memoria y paths
        cmd = [sys.executable, "-m", "src.models.inference"]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8', # Asegurar que leemos el subproceso en UTF-8
            errors='replace'  # Evitar crash si hay caracteres extraños
        )
        
        if result.returncode == 0:
            print("✅ Inferencia completada exitosamente.")
            # Mostrar las últimas líneas del log de inferencia para confirmación visual
            output_lines = result.stdout.strip().split('\n')
            if output_lines:
                print("   Último log de inferencia:")
                for line in output_lines[-3:]:
                    print(f"   -> {line}")
        else:
            print("❌ Error crítico en Inferencia:")
            print(result.stderr)
            # No lanzamos excepción aquí para permitir que el script termine limpiamente
            print("⚠️ El proceso continuará, pero revisa los logs de inferencia.")

        # ---------------------------------------------------------
        # RESUMEN FINAL
        # ---------------------------------------------------------
        elapsed = time.time() - start_time
        print(f"\n🎉 SINCRONIZACIÓN FINALIZADA en {elapsed:.2f} segundos.")
        print(" -> Base de datos Local: ACTUALIZADA")
        print(" -> Predicciones: DISPONIBLES")

    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO EN SYNC SYSTEM: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Sync System V2.0 Local')
    parser.add_argument('--force', action='store_true', help='Forzar re-entrenamiento completo e ignorar cache ETL')
    args = parser.parse_args()
    
    main(force_sync=args.force)