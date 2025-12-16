import sqlite3
import os
import glob
from src.etl.etl_pipeline import HipicaETL

def repair_etl():
    print("🔧 REPAIR ETL: Iniciando reparación de datos...")
    
    # 1. Identificar archivos recientes (últimos 7 días o específico)
    # Por seguridad, re-procesamos todos los PROGRAMA recenties.
    
    conn = sqlite3.connect('data/db/hipica_data.db')
    cursor = conn.cursor()
    
    # Reset flags for programs
    print("   🗑️  Limpiando tracking de archivos de Programa...")
    cursor.execute("DELETE FROM archivos_procesados WHERE nombre_archivo LIKE 'PROGRAMA%' OR nombre_archivo LIKE 'program%'")
    deleted = cursor.rowcount
    print(f"   ✓ {deleted} registros eliminados del tracking.")
    conn.commit()
    conn.close()
    
    # 2. Correr ETL normal (ahora procesará los archivos "nuevos")
    print("\n🚀 Ejecutando HipicaETL reparado...")
    etl = HipicaETL()
    etl.run()
    
    print("\n✅ Reparación completada.")

if __name__ == "__main__":
    repair_etl()
