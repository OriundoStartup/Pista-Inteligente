from src.models.train_v2 import HipicaLearner
from src.models.features_v2 import FeatureEngineering
import pandas as pd

def verify():
    print("--- 1. Loading Data ---")
    learner = HipicaLearner()
    df = learner.get_raw_data()
    print(f"Loaded {len(df)} rows.")
    print("Columns:", df.columns.tolist())
    
    print("\n--- 2. Running Feature Engineering V2 ---")
    fe = FeatureEngineering()
    fe.fit(df)
    df_transformed = fe.transform(df, is_training=True)
    
    print("\n--- 3. Verification ---")
    new_cols = ['duo_eff', 'sire_win_rate', 'track_win_rate', 'dist_win_rate', 'trend_3']
    
    # Check existence
    missing = [c for c in new_cols if c not in df_transformed.columns]
    if missing:
        print(f"❌ Missing columns: {missing}")
    else:
        print("✅ All new columns present.")
        
    # Check NaNs
    nans = df_transformed[new_cols].isna().sum()
    if nans.sum() > 0:
        print("❌ NaNs found:")
        print(nans[nans > 0])
    else:
        print("✅ No NaNs in new features.")
        
    # Show sample
    print("\n--- Sample Output (5 Rows) ---")
    print(df_transformed[new_cols + ['win_rate', 'races_count']].tail(5).to_string())

    # Manual Logic Check
    print("\n--- Logic Check: Cold Start ---")
    debutants = df_transformed[df_transformed['races_count'] == 0]
    if not debutants.empty:
        sample_deb = debutants.iloc[0]
        print(f"Debutant Win Rate: {sample_deb['win_rate']}")
        print(f"Debutant Sire Win Rate: {sample_deb['sire_win_rate']}")
        if sample_deb['win_rate'] == sample_deb['sire_win_rate']:
            print("✅ Cold Start Logic: Win Rate == Sire Win Rate for debutant.")
        else:
            print("⚠️ Cold Start Logic mismatch.")
    else:
        print("ℹ️ No debutants in tail sample to check.")

if __name__ == "__main__":
    verify()
