import json
import logging

try:
    with open('data/predicciones_activas.json', encoding='utf-8') as f:
        data = json.load(f)
        
    print(f"✅ Loaded {len(data)} predictions.")
    if len(data) > 0:
        sample = data[0]
        print(f"Sample keys: {list(sample.keys())}")
        print(f"Sample values: {sample}")
        
    # Verify no NaNs in critical fields
    errors = 0
    for p in data:
        if p['numero'] is None:
            errors += 1
            
    if errors == 0:
        print("✅ No NaNs found in 'numero' field.")
    else:
        print(f"❌ Found {errors} records with None in 'numero'.")

except Exception as e:
    print(f"❌ Error verifying JSON: {e}")
