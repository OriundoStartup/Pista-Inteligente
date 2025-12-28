"""
Test básico del Ensemble Ranker
Verifica que las importaciones funcionen correctamente
"""

import sys

print("🧪 Probando importaciones del Ensemble...\n")

# Test 1: Importar LightGBM
try:
    from lightgbm import LGBMRanker
    print("✅ LightGBM imported successfully")
except Exception as e:
    print(f"❌ LightGBM import failed: {e}")
    sys.exit(1)

# Test 2: Importar XGBoost
try:
    from xgboost import XGBRanker
    print("✅ XGBoost imported successfully")
except Exception as e:
    print(f"❌ XGBoost import failed: {e}")
    sys.exit(1)

# Test 3: Importar CatBoost (opcional)
try:
    from catboost import CatBoostRanker
    print("✅ CatBoost imported successfully")
    catboost_available = True
except Exception as e:
    print(f"⚠️  CatBoost not available (optional): {e}")
    catboost_available = False

# Test 4: Importar EnsembleRanker
try:
    from src.models.ensemble_ranker import EnsembleRanker
    print("✅ EnsembleRanker imported successfully")
except Exception as e:
    print(f"❌ EnsembleRanker import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Crear instancia del Ensemble
try:
    ensemble = EnsembleRanker(save_individual_models=False)
    print("✅ EnsembleRanker instance created")
    
    # Verificar modelos
    print(f"\n📊 Modelos base disponibles:")
    for name, model in zip(ensemble.base_model_names, ensemble.base_models):
        model_type = type(model).__name__
        print(f"   - {name:12s}: {model_type}")
    
except Exception as e:
    print(f"❌ Error creating EnsembleRanker: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
if catboost_available:
    print("✅ TODOS LOS TESTS PASARON (3 modelos)")
    print("   Ensemble completo: LightGBM + XGBoost + CatBoost")
else:
    print("✅ TESTS PASARON (2 modelos - CatBoost opcional)")
    print("   Ensemble funcional: LightGBM + XGBoost")
    print("   Nota: CatBoost no disponible pero el sistema funciona")
print("="*60)
