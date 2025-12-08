import os
import sys
import time
from src.etl.etl_pipeline import HipicaETL

def main():
    print("""
    ==================================================
       🏇 SISTEMA DE HÍPICA INTELIGENTE - SYNC V1 🏇
    ==================================================
    DETECTANDO ARCHIVOS EN /exports...
    """)
    
    start_time = time.time()
    
    try:
        # Inicializar y Correr ETL
        etl = HipicaETL()
        etl.run()
        
        elapsed = time.time() - start_time
        print(f"\n✅ SINCRONIZACIÓN COMPLETADA en {elapsed:.2f} segundos.")
        print(" -> La Base de Datos ha sido actualizada.")
        print(" -> Predicciones para programas futuros: LISTAS.")
        print(" -> Patrones de resultados (Quinelas/Trifectas): ACTUALIZADOS.")
        print("\n[INFO] Refresca tu navegador para ver los cambios.")
        
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        input("Presiona Enter para salir...")

if __name__ == "__main__":
    main()
