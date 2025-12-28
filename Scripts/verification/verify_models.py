
import os
import sys
import joblib
import pandas as pd
from pathlib import Path

# Add project root to path
sys.path.append(os.getcwd())

from src.models.features import FeatureEngineering
from src.models.data_manager import obtener_analisis_jornada

def verify_models():
    print("=== INICIANDO VERIFICACIÓN DE MODELOS ===")
    
    models_dir = Path("src/models")
    files_to_check = [
        "gb_model_v3.pkl",
        "rf_model_v2.pkl",
        "encoders_v2.pkl",
        "feature_eng_v2.pkl"
    ]
    
    status = {}
    
    # 1. Verification of file integrity and type
    for fname in files_to_check:
        fpath = models_dir / fname
        print(f"\nVerificando {fname}...")
        
        if not fpath.exists():
            print(f"❌ NO ENCONTRADO: {fname}")
            status[fname] = "MISSING"
            continue
            
        try:
            obj = joblib.load(fpath)
            print(f"✅ CARGADO EXITO: {type(obj)}")
            status[fname] = "OK_LOAD"
            
            # Additional checks
            if "model" in fname and hasattr(obj, "predict"):
                print("   ℹ️  Es un modelo predictivo válido (tiene método 'predict')")
            if "feature" in fname and hasattr(obj, "transform"):
                print("   ℹ️  Es un transformador válido (tiene método 'transform')")
                
        except Exception as e:
            print(f"❌ ERROR AL CARGAR: {e}")
            status[fname] = f"ERROR: {str(e)}"

    print("\n\n=== VERIFICACIÓN DE USO EN PREDICCIONES (INTEGRACIÓN) ===")
    try:
        print("Intentando generar análisis de jornada (lo que usa los modelos)...")
        # Esto usará los modelos definidos en data_manager.py (gb_model_v3 + feature_eng_v2)
        resultado = obtener_analisis_jornada()
        
        if isinstance(resultado, list):
             print(f"✅ INTEGRACIÓN EXITOSA. Se generó análisis para {len(resultado)} carreras/hipódromos.")
             if len(resultado) > 0:
                 print("   Ejemplo de predicción:")
                 try:
                     print(resultado[0].get('predicciones', [])[:2])
                 except: pass
        else:
             print("⚠️  INTEGRACIÓN DUDOSA. El resultado no es una lista.")
             
    except Exception as e:
        print(f"❌ ERROR EN INTEGRACIÓN: {e}")
        import traceback
        traceback.print_exc()

    print("\n=== RESUMEN FINAL ===")
    for k, v in status.items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    verify_models()
