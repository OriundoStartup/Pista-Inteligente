import sys
import os
import logging
import pandas as pd
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.models.feature_store import FeatureStore
from src.models.data_manager import cargar_datos_3nf

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("UpdateStore")

def main():
    logger.info("Starting Feature Store Incremental Update...")
    
    # 1. Load Store
    store_path = 'data/feature_store.pkl'
    if not os.path.exists(store_path):
        logger.error(f"Store not found at {store_path}. Run init_feature_store.py first.")
        return

    store = FeatureStore.load(store_path)
    last_updated = store.last_updated
    
    if not last_updated:
        logger.warning("Store has no last_updated date. Running full init suggested.")
        # Fallback to init script logic or just continue from very old date
        last_updated = datetime(2020, 1, 1)
        
    logger.info(f"Store last updated: {last_updated}")
    
    # 2. Fetch New Data (Since last updated)
    # cargar_datos_3nf loads EVERYTHING. In 3NF, we can filter by date in SQL ideally.
    # But existing function loads all. Optimization: Modify data_manager or filter DF.
    # For now (8k rows), filtering DF is fine.
    
    df_all = cargar_datos_3nf()
    if df_all.empty:
        logger.info("No data found in DB.")
        return
        
    df_all['fecha'] = pd.to_datetime(df_all['fecha'])
    
    # Filter: Races AFTER last_updated
    # Safety margin: Look back 1 day just in case of timezone issues?
    # Better to be idempotent: FeatureStore.update implies adding *new* stats.
    # If we add the same race twice, wins/runs will double count!
    # FeatureStore logic is simple "+= 1".
    # CRITICAL: We need to ensure we don't process same race twice.
    # We should iterate and check if race is already processed? 
    # Or rely on strict date filtering.
    
    cutoff_date = last_updated
    new_data = df_all[df_all['fecha'] > cutoff_date].copy()
    
    if new_data.empty:
        logger.info("✅ Feature Store is already up to date. No new races found.")
        return
        
    logger.info(f"Found {len(new_data)} new results to process.")
    
    # 3. Update
    store.update(new_data)
    
    # 4. Save
    store.save(store_path)
    logger.info(f"✅ Feature Store updated and saved.")
    logger.info(f"   New last_updated: {store.last_updated}")

if __name__ == "__main__":
    main()
