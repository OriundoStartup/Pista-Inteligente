import sys
import os
import logging
import pandas as pd

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.models.feature_store import FeatureStore

def header(msg):
    print("\n" + "="*50)
    print(msg)
    print("="*50)

def main():
    store = FeatureStore.load('data/feature_store.pkl')
    
    header("Feature Store Inspection")
    print(f"Horses tracked: {len(store.horse_stats):,}")
    print(f"Jockey-Trainer pairs: {len(store.duo_stats):,}")
    print(f"Sires tracked: {len(store.sire_stats):,}")
    
    # Check a few horses
    header("Sample Horse Features")
    
    # Get top 3 horses by races run
    top_horses = sorted(
        store.horse_stats.items(), 
        key=lambda x: x[1]['total_races'], 
        reverse=True
    )[:3]
    
    for h_id, stats in top_horses:
        print(f"Horse ID: {h_id}")
        print(f"  Races: {stats['total_races']}")
        print(f"  Wins: {stats['total_wins']}")
        win_rate = stats['total_wins'] / stats['total_races'] if stats['total_races'] > 0 else 0
        print(f"  Win Rate: {win_rate:.2%}")
        print(f"  Last Date: {stats['last_date']}")
        print(f"  Last 3 Speeds: {[round(s, 2) for s in stats['last_3_speeds']]}")
        print("-" * 30)
        
        # Validation checks
        if not (0 <= win_rate <= 1.0):
            print("  ❌ ERROR: Win Rate out of bounds")
        if stats['total_races'] < 0:
             print("  ❌ ERROR: Negative races")
             
    header("Sanity Checks")
    errors = 0
    # Check random sample of 100 horses
    import random
    keys = list(store.horse_stats.keys())
    sample_keys = random.sample(keys, min(100, len(keys)))
    
    for k in sample_keys:
        stats = store.horse_stats[k]
        if stats['total_wins'] > stats['total_races']:
            print(f"❌ Error for Horse {k}: Wins > Races")
            errors += 1
            
    if errors == 0:
        print("✅ Random sample check passed: Wins <= Races for all sampled horses.")
    else:
        print(f"❌ Found {errors} inconsistencies.")

if __name__ == "__main__":
    main()
