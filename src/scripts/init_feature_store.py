import sys
import os
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.models.feature_store import FeatureStore
from src.models.data_manager import cargar_datos_3nf

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('InitFeatureStore')

def main():
    logger.info("Initializing Feature Store from History...")
    
    # 1. Load History
    logger.info("Loading historical data (3NF)...")
    df = cargar_datos_3nf()
    
    if df.empty:
        logger.error("❌ No historical data found. Cannot initialize store.")
        sys.exit(1)
        
    logger.info(f"Loaded {len(df):,} records.")
    
    # 2. Init Store
    store = FeatureStore()
    
    # 3. Populate
    logger.info("Populating store (this may take a minute)...")
    store.update(df)
    
    # 4. Save
    output_path = 'data/feature_store.pkl'
    store.save(output_path)
    
    logger.info("✅ Feature Store initialized and saved.")
    
    # Verify
    n_horses = len(store.horse_stats)
    logger.info(f"Stats: {n_horses:,} horses tracked.")

if __name__ == "__main__":
    main()
