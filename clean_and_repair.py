import sqlite3
from src.etl.etl_pipeline import HipicaETL

def clean_and_repair():
    print("🧹 CLEAN & REPAIR: Borrando datos del 18 de Dic para regenerar...")
    conn = sqlite3.connect('data/db/hipica_data.db')
    cursor = conn.cursor()
    
    # 1. Borrar datos de programa existentes para esa fecha
    cursor.execute("DELETE FROM programa_carreras WHERE fecha = '2025-12-18'")
    deleted_prog = cursor.rowcount
    print(f"   ✓ Borrados {deleted_prog} registros de 'programa_carreras' (2025-12-18).")
    
    # 2. Borrar predicciones asociadas
    cursor.execute("DELETE FROM predicciones WHERE fecha_carrera = '2025-12-18'")
    deleted_pred = cursor.rowcount
    print(f"   ✓ Borradas {deleted_pred} predicciones antiguas (2025-12-18).")
    
    # 3. Borrar tracking del archivo para obligar a re-procesar
    cursor.execute("DELETE FROM archivos_procesados WHERE nombre_archivo LIKE '%2025-12-18%'")
    deleted_track = cursor.rowcount
    print(f"   ✓ Reset tracking para {deleted_track} archivo(s).")
    
    conn.commit()
    conn.close()
    
    # 4. Ejecutar ETL
    print("\n🚀 Re-ejecutando ETL...")
    etl = HipicaETL()
    etl.run()
    print("\n✅ Proceso Finalizado.")

if __name__ == "__main__":
    clean_and_repair()
