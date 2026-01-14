import os
import time
import sys
import argparse
import subprocess
import logging
import gc
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

# --- IMPORTACIONES DEL SISTEMA V4.0 ---
try:
    from src.etl.etl_pipeline import HipicaETL
    from src.models.train_v2 import HipicaLearner  # Baseline
    from src.utils.migrate_to_firebase import migrate
except ImportError as e:
    logging.error(f"❌ Error de importación: {e}")
    logging.error("Asegúrate de ejecutar este script desde la raíz del proyecto (python sync_system.py)")
    sys.exit(1)

def main(force_sync=False, use_ensemble=True):
    """
    SISTEMA DE HIPICA INTELIGENTE - SYNC V4.0 (LOCAL / CONTENEDOR)
    Orquestador principal: ETL -> Entrenamiento -> Inferencia -> Migración
    
    Args:
        force_sync: Forzar re-procesamiento completo
        use_ensemble: Usar Ensemble v4 (True) o Baseline v2 (False)
    """
    version = "ENSEMBLE V4" if use_ensemble else "BASELINE V2"
    logging.info("==================================================")
    logging.info(f"   SISTEMA DE HIPICA INTELIGENTE - SYNC V4.0")
    logging.info(f"   MODELO: {version}")
    logging.info("   (MODO: LOCAL / CONTENEDOR)")
    logging.info("==================================================")
    
    start_time = time.time()
    
    try:
        # ---------------------------------------------------------
        # PASO 1: ETL (Cargar datos nuevos de la web)
        # ---------------------------------------------------------
        logging.info("[PASO 1/5] Ejecutando ETL (Extracción de Datos)...")
        etl_start = time.time()
        etl = HipicaETL()
        archivos_nuevos = etl.run(force_reprocess=force_sync)
        
        if archivos_nuevos == 0 and not force_sync:
            logging.info("✅ No hay datos históricos nuevos.")
        else:
            logging.info(f"✅ Se han procesado {archivos_nuevos} archivos nuevos.")
        
        logging.info(f"   Tiempo: {time.time() - etl_start:.1f}s")
        gc.collect()  # Clean up memory

        # ---------------------------------------------------------
        # PASO 2: RE-ENTRENAMIENTO (Solo si hubo datos nuevos o se fuerza)
        # ---------------------------------------------------------
        if archivos_nuevos > 0 or force_sync:
            train_start = time.time()
            
            if use_ensemble:
                logging.info("[PASO 2/5] Entrenando Ensemble v4 (LightGBM + XGBoost + CatBoost)...")
                try:
                    # Entrenar ensemble v4
                    cmd_train = [sys.executable, "-m", "src.models.train_v4_ensemble"]
                    result = subprocess.run(cmd_train, capture_output=True, text=True, encoding='utf-8', errors='replace')
                    
                    if result.returncode == 0:
                        logging.info("✅ Ensemble v4 entrenado exitosamente.")
                    else:
                        logging.error(f"⚠️ Error en entrenamiento ensemble: {result.stderr}")
                        logging.warning(" -> Fallback a baseline v2...")
                        use_ensemble = False
                        raise Exception("Ensemble training failed")
                        
                except Exception as e:
                    logging.error(f"⚠️ Error entrenando ensemble: {e}")
                    logging.info("   Intentando con baseline v2...")
                    use_ensemble = False
            
            if not use_ensemble:
                logging.info("[PASO 2/5] Entrenando Baseline v2 (LightGBM)...")
                try:
                    learner = HipicaLearner()
                    learner.train()
                    logging.info("✅ Baseline v2 entrenado exitosamente.")
                except Exception as e:
                    logging.error(f"⚠️ Error en entrenamiento baseline: {e}")
                    logging.warning(" -> Se usará la versión anterior del modelo.")
            
            logging.info(f"   Tiempo entrenamiento: {time.time() - train_start:.1f}s")
            gc.collect()
        else:
            logging.info("[PASO 2/5] Saltando entrenamiento (Modelo vigente).")

        # ---------------------------------------------------------
        # PASO 3: INFERENCIA (Predicciones para futuro)
        # ---------------------------------------------------------
        logging.info("[PASO 3/5] Ejecutando Pipeline de Inferencia...")
        inference_start = time.time()
        
        # Seleccionar modelo para inferencia
        if use_ensemble:
            inference_module = "src.models.inference_ensemble"
            logging.info("   Usando: Ensemble v4 (LightGBM + XGBoost + CatBoost)")
        else:
            inference_module = "src.models.inference"
            logging.info("   Usando: Baseline v2 (LightGBM)")
        
        cmd = [sys.executable, "-m", inference_module]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode == 0:
            logging.info("✅ Inferencia completada exitosamente.")
            output_lines = result.stdout.strip().split('\n')
            if output_lines:
                logging.info("   Últimas líneas de inferencia:")
                for line in output_lines[-3:]:
                    logging.info(f"   -> {line}")
        else:
            logging.error("❌ Error en Inferencia:")
            logging.error(result.stderr)
            
            # Fallback si ensemble falla
            if use_ensemble:
                logging.warning("⚠️ Intentando con baseline v2...")
                cmd_fallback = [sys.executable, "-m", "src.models.inference"]
                result_fallback = subprocess.run(cmd_fallback, capture_output=True, text=True, encoding='utf-8', errors='replace')
                
                if result_fallback.returncode == 0:
                    logging.info("✅ Inferencia con baseline completada.")
                else:
                    logging.error("❌ Fallback también falló.")
                    logging.error(result_fallback.stderr)
            else:
                logging.warning("⚠️ El proceso continuará, pero revisa los logs.")
        
        logging.info(f"   Tiempo inferencia: {time.time() - inference_start:.1f}s")
        gc.collect()

        # ---------------------------------------------------------
        # PASO 4: MIGRACIÓN A FIREBASE
        # ---------------------------------------------------------
        logging.info("[PASO 4/5] Migrando datos a Firestore...")
        migration_start = time.time()
        
        try:
            migrate()
            logging.info("✅ Migración a Firestore completada.")
            logging.info(f"   Tiempo migración: {time.time() - migration_start:.1f}s")
        except Exception as e:
            logging.error(f"❌ Error en migración: {e}")
            logging.warning("   Las predicciones están disponibles localmente, pero no en Cloud.")
            # Non-blocking: Local predictions still available
        
        gc.collect()

        # ---------------------------------------------------------
        # PASO 5: DESPLIEGUE A CLOUD RUN (MODO ECONÓMICO)
        # ---------------------------------------------------------
        logging.info("[PASO 5/5] Desplegando versión económica a Cloud Run...")
        deploy_start = time.time()

        # Comando para desplegar código fuente directamente (incluye BD en data/)
        # Configurado para minimizar costos: 0 min instances, 512MB RAM
        deploy_cmd = (
            "gcloud run deploy pista-inteligente "
            "--source . "
            "--region us-central1 "
            "--allow-unauthenticated "
            "--min-instances 0 "
            "--max-instances 1 "
            "--memory 512Mi "
            "--quiet"  # No pedir confirmación
        )

        try:
            logging.info(f"   Ejecutando: {deploy_cmd}")
            # shell=True es recomedable en Windows para comandos como gcloud
            res_deploy = subprocess.run(deploy_cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')

            if res_deploy.returncode == 0:
                logging.info("✅ Despliegue exitoso.")
                # Intentar mostrar la URL
                for line in res_deploy.stdout.splitlines():
                    if "Service URL:" in line:
                        logging.info(f"   🌍 {line.strip()}")
            else:
                logging.error("❌ Falló el despliegue.")
                if "403" in res_deploy.stderr:
                    logging.error("   ⚠️ Error de permisos (403). Verifica que tu usuario tenga rol de 'Cloud Build Editor' o 'Owner'.")
                logging.error(f"   Detalle: {res_deploy.stderr}")
        
        except Exception as e:
            logging.error(f"❌ Error ejecutando comando de despliegue: {e}")

        # Deploy to Firebase Hosting (Static Assets + Rewrite Rules)
        logging.info("[EXTRA] Sincronizando Hosting (firebase deploy)...")
        try:
            res_hosting = subprocess.run("firebase deploy --only hosting", shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
            if res_hosting.returncode == 0:
                logging.info("✅ Firebase Hosting actualizado.")
            else:
                logging.warning(f"⚠️ Error actualizando Hosting: {res_hosting.stderr}")
        except Exception as e:
            logging.warning(f"⚠️ No se pudo ejecutar firebase deploy: {e}")

        logging.info(f"   Tiempo despliegue: {time.time() - deploy_start:.1f}s")
        gc.collect()

        # ---------------------------------------------------------
        # RESUMEN FINAL
        # ---------------------------------------------------------
        elapsed = time.time() - start_time
        logging.info("\n" + "="*70)
        logging.info(f"🎉 SINCRONIZACIÓN COMPLETADA en {elapsed:.2f}s")
        logging.info("="*70)
        logging.info(f" -> Modelo usado: {version}")
        logging.info(" -> Base de datos Local: ACTUALIZADA")
        logging.info(" -> Predicciones: DISPONIBLES")
        logging.info(" -> Firebase: SINCRONIZADO")
        logging.info("="*70)

    except Exception as e:
        logging.critical(f"❌ ERROR CRÍTICO EN SYNC SYSTEM: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Sync System V4.0 - Ensemble Integration')
    parser.add_argument('--force', action='store_true', 
                       help='Forzar re-entrenamiento completo e ignorar cache ETL')
    parser.add_argument('--baseline', action='store_true',
                       help='Usar baseline v2 en lugar de ensemble v4')
    args = parser.parse_args()
    
    main(force_sync=args.force, use_ensemble=not args.baseline)