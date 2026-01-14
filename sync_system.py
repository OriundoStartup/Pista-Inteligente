import sys
import os
import time
import logging
import argparse
import requests

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def trigger_vercel_redeploy():
    """
    Dispara un redeploy en Vercel usando un Deploy Hook.
    Configura VERCEL_DEPLOY_HOOK en tu .env con el webhook de tu proyecto.
    """
    deploy_hook = os.getenv('VERCEL_DEPLOY_HOOK')
    if not deploy_hook:
        logging.warning("⚠️ VERCEL_DEPLOY_HOOK no configurado. Salta el redeploy automático.")
        logging.info("   Para activar: crea un Deploy Hook en Vercel > Settings > Git > Deploy Hooks")
        return False
    
    try:
        response = requests.post(deploy_hook, timeout=30)
        if response.status_code == 200 or response.status_code == 201:
            logging.info("✅ Vercel redeploy disparado exitosamente!")
            return True
        else:
            logging.warning(f"⚠️ Vercel respondió con código {response.status_code}")
            return False
    except Exception as e:
        logging.error(f"❌ Error al disparar redeploy de Vercel: {e}")
        return False

def main(force_sync=False):
    """
    SISTEMA DE HIPICA INTELIGENTE - SYNC V4.2 (SUPABASE + VERCEL)
    Orquestador principal: CSV -> SQLite -> Supabase -> (Opcional) Vercel Redeploy
    """
    logging.info("==================================================")
    logging.info("   SISTEMA DE HIPICA INTELIGENTE - SYNC V4.2")
    logging.info("   TARGET: SUPABASE (DB) + VERCEL (Frontend)")
    logging.info("==================================================")
    
    start_time = time.time()
    
    # ---------------------------------------------------------
    # PASO 1: ETL (CSV -> SQLite)
    # ---------------------------------------------------------
    logging.info("\n[PASO 1/4] Ejecutando ETL (Extracción de CSVs)...")
    try:
        from src.etl.etl_pipeline import HipicaETL
        etl = HipicaETL()
        archivos_nuevos = etl.run(force_reprocess=force_sync)
        
        if archivos_nuevos == 0 and not force_sync:
            logging.info("✅ No hay archivos CSV nuevos para procesar.")
        else:
            logging.info(f"✅ Se han procesado {archivos_nuevos} archivos nuevos en SQLite.")
            
    except Exception as e:
        logging.critical(f"❌ Error en ETL: {e}")
        sys.exit(1)

    # ---------------------------------------------------------
    # PASO 2: MIGRACIÓN (SQLite -> Supabase)
    # ---------------------------------------------------------
    logging.info("\n[PASO 2/4] Sincronizando SQLite -> Supabase...")
    try:
        from src.utils.migrate_sqlite_to_supabase import run_migration
        run_migration()
        logging.info("✅ Sincronización con Supabase completada.")
        
    except Exception as e:
        logging.critical(f"❌ Error en Migración a Supabase: {e}")
        logging.info("   Asegúrate de tener SUPABASE_URL y KEY en tu .env")
        sys.exit(1)

    # ---------------------------------------------------------
    # PASO 3: INFERENCIA (Generar Predicciones)
    # ---------------------------------------------------------
    logging.info("\n[PASO 3/4] Ejecutando Inferencia sobre datos de Supabase...")
    try:
        from src.scripts.daily_inference_job import SupabaseMigrationWorker
        
        worker = SupabaseMigrationWorker()
        logging.info("   -> Re-validando programas y generando predicciones...")
        worker.run_ingestion_pipeline()
        logging.info("✅ Predicciones generadas y guardadas en Supabase.")
        
    except Exception as e:
        logging.error(f"❌ Error en Inferencia: {e}")
        # No fatal, los datos ya están subidos.

    # ---------------------------------------------------------
    # PASO 4: REDEPLOY VERCEL (Opcional)
    # ---------------------------------------------------------
    logging.info("\n[PASO 4/4] Disparando redeploy en Vercel (si configurado)...")
    trigger_vercel_redeploy()

    logging.info("\n" + "="*70)
    logging.info(f"🎉 PROCESO COMPLETADO en {time.time() - start_time:.2f}s")
    logging.info("   Los datos deberían estar visibles en tu sitio Vercel.")
    logging.info("="*70)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--force', action='store_true', help='Forzar re-procesamiento de CSVs')
    args = parser.parse_args()
    
    main(force_sync=args.force)