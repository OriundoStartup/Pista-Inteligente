import sys
import os
import time
import logging
import argparse

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main(force_sync=False):
    """
    SISTEMA DE HIPICA INTELIGENTE - SYNC V4.1 (SUPABASE EDITION)
    Orquestador principal: CSV -> SQLite -> Supabase -> Inferencia
    """
    logging.info("==================================================")
    logging.info("   SISTEMA DE HIPICA INTELIGENTE - SYNC V4.1")
    logging.info("   TARGET: SUPABASE (Vercel Backend)")
    logging.info("==================================================")
    
    start_time = time.time()
    
    # ---------------------------------------------------------
    # PASO 1: ETL (CSV -> SQLite)
    # ---------------------------------------------------------
    logging.info("\n[PASO 1/3] Ejecutando ETL (Extracción de CSVs)...")
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
    logging.info("\n[PASO 2/3] Sincronizando SQLite -> Supabase...")
    try:
        from src.utils.migrate_sqlite_to_supabase import run_migration
        # Nota: run_migration() actualmente migra TODO. 
        # Idealmente se optimizaría para migrar solo deltas, pero el upsert lo maneja.
        run_migration()
        logging.info("✅ Sincronización con Supabase completada.")
        
    except Exception as e:
        logging.critical(f"❌ Error en Migración a Supabase: {e}")
        logging.info("Asegúrate de tener SUPABASE_URL y KEY en tu .env")
        sys.exit(1)

    # ---------------------------------------------------------
    # PASO 3: INFERENCIA (Supabase -> Predicciones)
    # ---------------------------------------------------------
    logging.info("\n[PASO 3/3] Ejecutando Inferencia sobre datos de Supabase...")
    try:
        from src.scripts.daily_inference_job import SupabaseMigrationWorker
        
        worker = SupabaseMigrationWorker()
        # En lugar de scrapear web (ingest_races), usamos lo que ya subimos (programs)
        # Pero el worker actual está diseñado para scrapear.
        # Vamos a llamar a 'run_inference' directamente si podemos reconstruir el DF del programa.
        
        # HACK: Por ahora, el worker scrapea de nuevo para tener el DF en memoria rapido.
        # Idealmente leemos de supabase.
        # Pero como acabamos de subir los programas, "ingest_races" del worker funcionará idempotentemente.
        
        logging.info("   -> Re-validando programas y generando predicciones...")
        # Llama al flujo completo del worker (Scrape Future + Inference)
        # Esto asegura que tengamos el DF con los IDs correctos para predecir
        worker.run_ingestion_pipeline() 
        # Nota: Si el programa YA estaba en CSV, el scraper web lo volverá a bajar. 
        # Si queremos usar SOLO el CSV, tendríamos que adaptar el worker.
        # PERO: Los CSVs ya subidos a Supabase por Paso 2 ya están ahí.
        
        # TODO: Refactorizar worker para leer 'Programas Futuros' desde DB.
        # Por ahora, corremos el worker estándar que baja de la web para asegurar frescura.
        
    except Exception as e:
        logging.error(f"❌ Error en Inferencia: {e}")
        # No fatal, los datos ya están subidos.

    logging.info("\n" + "="*70)
    logging.info(f"🎉 PROCESO COMPLETADO en {time.time() - start_time:.2f}s")
    logging.info("   Los datos deberían estar visibles en Vercel.")
    logging.info("="*70)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--force', action='store_true', help='Forzar re-procesamiento de CSVs')
    args = parser.parse_args()
    
    main(force_sync=args.force)