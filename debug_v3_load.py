import joblib
import os
import sys

# Add current dir to path to find src
sys.path.append(os.getcwd())

from src.models.features import FeatureEngineering

print("🔍 Verificando carga de modelo V3...")

model_path = 'src/models/gb_model_v3.pkl'
fe_path = 'src/models/feature_eng_v2.pkl'

if not os.path.exists(model_path):
    print(f"❌ Error: No existe {model_path}")
    sys.exit(1)

try:
    print(f"   Intentando cargar {model_path}...")
    model = joblib.load(model_path)
    print(f"   ✅ Modelo cargado: {type(model)}")
except Exception as e:
    print(f"❌ Error cargando modelo: {e}")
    import traceback
    traceback.print_exc()

try:
    print(f"   Intentando cargar {fe_path}...")
    fe = FeatureEngineering.load(fe_path)
    print(f"   ✅ Feature Engineering cargado.")
except Exception as e:
    print(f"❌ Error cargando FE: {e}")
    import traceback
    traceback.print_exc()
