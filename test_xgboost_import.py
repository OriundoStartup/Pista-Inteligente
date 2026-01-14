import sys
import os
sys.path.append(os.getcwd())

print(f"Python executable: {sys.executable}")
try:
    import xgboost
    print(f"XGBoost version: {xgboost.__version__}")
    from xgboost import XGBRanker
    print("XGBRanker imported successfully")
except ImportError as e:
    print(f"Error importing XGBRanker: {e}")
    sys.exit(1)

try:
    from src.models.ensemble_ranker import EnsembleRanker
    print("EnsembleRanker imported successfully")
except ImportError as e:
    print(f"Error importing EnsembleRanker: {e}")
    sys.exit(1)
