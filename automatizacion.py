"""
Script de automatización para ejecutar scraping y predicciones diariamente.
Ejecutar este script antes de cada jornada de carreras.
"""

import subprocess
import sys
from datetime import datetime
import sqlite3
import pandas as pd

def log(mensaje):
    """Imprime mensaje con timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {mensaje}")

def ejecutar_scraping():
    """Ejecuta el scraper para obtener datos actualizados."""
    log("[INFO] Iniciando scraping de datos...")
    try:
        result = subprocess.run(
            [sys.executable, "scraper.py"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos máximo
        )
        
        if result.returncode == 0:
            log("[OK] Scraping completado exitosamente")
            return True
        else:
            log(f"[WARN] Scraping completado con advertencias: {result.stderr}")
            return True  # Continuar aunque haya advertencias
    except Exception as e:
        log(f"[ERROR] Error en scraping: {e}")
        return False

def ejecutar_predicciones():
    """Ejecuta el modelo de ML para generar predicciones."""
    log("[INFO] Generando predicciones con Machine Learning...")
    try:
        result = subprocess.run(
            [sys.executable, "predictor_ml.py"],
            capture_output=True,
            text=True,
            timeout=120  # 2 minutos máximo
        )
        
        if result.returncode == 0:
            log("[OK] Predicciones generadas exitosamente")
            print(result.stdout)  # Mostrar salida del predictor
            return True
        else:
            log(f"[ERROR] Error al generar predicciones: {result.stderr}")
            return False
    except Exception as e:
        log(f"[ERROR] Error en predicciones: {e}")
        return False

def verificar_datos():
    """Verifica que hay datos en la base de datos."""
    try:
        conn = sqlite3.connect('hipica_data.db')
        
        # Verificar resultados históricos
        df_resultados = pd.read_sql("SELECT COUNT(*) as count FROM resultados", conn)
        count_resultados = df_resultados['count'][0]
        
        # Verificar programa
        try:
            df_programa = pd.read_sql("SELECT COUNT(*) as count FROM programa_carreras", conn)
            count_programa = df_programa['count'][0]
        except:
            count_programa = 0
        
        # Verificar predicciones
        try:
            df_predicciones = pd.read_sql("SELECT COUNT(*) as count FROM predicciones", conn)
            count_predicciones = df_predicciones['count'][0]
        except:
            count_predicciones = 0
        
        conn.close()
        
        log(f"[INFO] Estado de la base de datos:")
        log(f"   - Resultados históricos: {count_resultados}")
        log(f"   - Carreras programadas: {count_programa}")
        log(f"   - Predicciones generadas: {count_predicciones}")
        
        return count_resultados > 0
        
    except Exception as e:
        log(f"[ERROR] Error al verificar datos: {e}")
        return False

def main():
    """Función principal de automatización."""
    log("="*60)
    log("AUTOMATIZACIÓN PISTA INTELIGENTE")
    log("="*60)
    
    # Paso 1: Ejecutar scraping
    if not ejecutar_scraping():
        log("[ERROR] Falló el scraping. Abortando automatización.")
        return False
    
    # Paso 2: Verificar datos
    if not verificar_datos():
        log("[WARN] No hay suficientes datos en la base de datos.")
        return False
    
    # Paso 3: Generar predicciones
    if not ejecutar_predicciones():
        log("[WARN] No se pudieron generar predicciones, pero los datos están actualizados.")
        return True  # No es crítico si fallan las predicciones
    
    log("="*60)
    log("[OK] AUTOMATIZACIÓN COMPLETADA EXITOSAMENTE")
    log("="*60)
    log("La aplicación está lista para mostrar las predicciones.")
    
    return True

if __name__ == "__main__":
    exito = main()
    sys.exit(0 if exito else 1)
