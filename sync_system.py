import os
import time
import sys
import argparse
import subprocess
import logging
from datetime import datetime

# --- CONFIGURACIÓN DE LOGGING ---
# Configurar logging para escribir en archivo y consola
log_filename = "sync.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# --- FIX PARA WINDOWS/EMOJIS ---
# Fuerza la salida de la consola a UTF-8 para evitar UnicodeEncodeError
if sys.platform == "win32" and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# --- IMPORTACIONES DEL SISTEMA V2.0 ---
try:
    from src.etl.etl_pipeline import HipicaETL
    from src.models.train_v2 import HipicaLearner
    from src.utils.migrate_to_firebase import migrate # Import migration logic
except ImportError as e:
    logging.error(f"❌ Error de importación: {e}")
    logging.error("Asegúrate de ejecutar este script desde la raíz del proyecto (python sync_system.py)")
    sys.exit(1)

def main(force_sync=False):
    """
    SISTEMA DE HIPICA INTELIGENTE - SYNC V2.0 (LOCAL / CONTENEDOR)
    Orquestador principal: ETL -> Entrenamiento -> Inferencia
    """
    logging.info("==================================================")
    logging.info("   SISTEMA DE HIPICA INTELIGENTE - SYNC V2.0")
    logging.info("   (MODO: LOCAL / CONTENEDOR)")
    logging.info("==================================================")
    
    start_time = time.time()
    
    try:
        # ---------------------------------------------------------
        # PASO 1: ETL (Cargar datos nuevos de la web)
        # ---------------------------------------------------------
        logging.info("[PASO 1/3] Ejecutando ETL (Extracción de Datos)...")
        etl = HipicaETL()
        # force_reprocess permite bajar todo de nuevo si es necesario
        archivos_nuevos = etl.run(force_reprocess=force_sync)
        
        if archivos_nuevos == 0 and not force_sync:
            logging.info("✅ No hay datos históricos nuevos.")
        else:
            logging.info(f"✅ Se han procesado {archivos_nuevos} archivos nuevos.")

        # ---------------------------------------------------------
        # PASO 2: RE-ENTRENAMIENTO (Solo si hubo datos nuevos o se fuerza)
        # ---------------------------------------------------------
        # Si llegaron resultados nuevos, el modelo debe aprender de ellos.
        if archivos_nuevos > 0 or force_sync:
            logging.info("[PASO 2/3] Entrenando Modelo 'Learning to Rank' (LGBM)...")
            try:
                learner = HipicaLearner()
                learner.train() # Genera lgbm_ranker_v1.pkl
                logging.info("✅ Modelo re-entrenado exitosamente.")
            except Exception as e:
                logging.error(f"⚠️ Error en entrenamiento: {e}")
                logging.warning(" -> Se usará la versión anterior del modelo.")
        else:
            logging.info("[PASO 2/3] Saltando entrenamiento (Modelo vigente).")

        # ---------------------------------------------------------
        # PASO 3: INFERENCIA (Predicciones para mañana)
        # ---------------------------------------------------------
        # Siempre ejecutamos inferencia, porque puede haber programas nuevos para mañana
        logging.info("[PASO 3/3] Ejecutando Pipeline de Inferencia...")
        
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
            logging.info("✅ Inferencia completada exitosamente.")
            # Mostrar las últimas líneas del log de inferencia para confirmación visual
            output_lines = result.stdout.strip().split('\n')
            if output_lines:
                logging.info("   Último log de inferencia:")
                for line in output_lines[-3:]:
                    logging.info(f"   -> {line}")
        else:
            logging.error("❌ Error crítico en Inferencia:")
            logging.error(result.stderr)
            # No lanzamos excepción aquí para permitir que el script termine limpiamente
            logging.warning("⚠️ El proceso continuará, pero revisa los logs de inferencia.")

        # ---------------------------------------------------------
        # PASO 4: MIGRACIÓN A FIREBASE (Phase 4 Integration)
        # ---------------------------------------------------------
        # Ahora que tenemos nuevas predicciones y datos, subimos todo a Firestore.
        logging.info("[PASO 4/4] Migrando datos a Firestore...")
        try:
            migrate()
            logging.info("✅ Migración a Firestore completada.")
        except Exception as e:
            logging.error(f"❌ Error en migración: {e}")
            # Non-blocking error for local sync, but critical for deployment
            pass

        # ---------------------------------------------------------
        # RESUMEN FINAL
        # ---------------------------------------------------------
        elapsed = time.time() - start_time
        logging.info(f"🎉 SINCRONIZACIÓN FINALIZADA en {elapsed:.2f} segundos.")
        logging.info(" -> Base de datos Local: ACTUALIZADA")
        logging.info(" -> Predicciones: DISPONIBLES")

    except Exception as e:
        logging.critical(f"❌ ERROR CRÍTICO EN SYNC SYSTEM: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Sync System V2.0 Local')
    parser.add_argument('--force', action='store_true', help='Forzar re-entrenamiento completo e ignorar cache ETL')
    args = parser.parse_args()
    
    main(force_sync=args.force)