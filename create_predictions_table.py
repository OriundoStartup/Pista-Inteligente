"""Script simple para crear la tabla de predicciones"""
from src.etl.etl_pipeline import HipicaETL

print("Inicializando ETL...")
etl = HipicaETL()
print("✅ Tabla de predicciones creada exitosamente")
