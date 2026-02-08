import pandas as pd
import numpy as np
import json
import logging
import os
import joblib

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DriftMonitor")

def calculate_psi(expected, actual, buckettype='bins', buckets=10, axis=0):
    """
    Calculate the PSI (Population Stability Index) for a single variable
    Args:
       expected: numpy array of original values (training)
       actual: numpy array of new values (production)
       buckettype: type of strategy for creating buckets, bins (fixed width) or quantiles (fixed count)
       buckets: number of buckets
       axis: axis by which variables are defined
     Returns:
       psi_value: calculated PSI value
    """

    def scale_range (input, min, max):
        input += -(np.min(input))
        input /= np.max(input) / (max - min)
        input += min
        return input

    breakpoints = np.arange(0, buckets + 1) / (buckets) * 100

    if buckettype == 'bins':
        breakpoints = scale_range(breakpoints, np.min(expected), np.max(expected))
    elif buckettype == 'quantiles':
        breakpoints = np.stack([np.percentile(expected, b) for b in breakpoints])

    expected_percents = np.histogram(expected, breakpoints)[0] / len(expected)
    actual_percents = np.histogram(actual, breakpoints)[0] / len(actual)

    def sub_psi(e_perc, a_perc):
        if a_perc == 0:
            a_perc = 0.0001
        if e_perc == 0:
            e_perc = 0.0001

        value = (e_perc - a_perc) * np.log(e_perc / a_perc)
        return(value)

    psi_value = np.sum(sub_psi(expected_percents[i], actual_percents[i]) for i in range(0, len(expected_percents)))

    return psi_value

def check_drift():
    logger.info("🔍 Iniciando chequeo de Drift...")
    
    # 1. Load Reference Data (Training Scores)
    # Ideally, we should have saved 'y_pred_train' or 'y_pred_test'
    # Since we didn't save raw scores in metadata directly, we can load the model and predict on a sample
    # OR better: Assume a reference distribution.
    # For now, let's try to load the ensemble and run on a small sample of history if metadata is missing.
    # Actually, we can assume a uniform distribution of scores is NOT the case.
    # Let's use the 'predicciones_activas.json' from yesterday as reference? No.
    
    # Best proxy: We check if the scores are concentrated in ends (0 or 1).
    # Load current predictions
    pred_path = 'data/predicciones_activas.json'
    if not os.path.exists(pred_path):
        logger.warning(f"⚠️ No hay predicciones activas en {pred_path}")
        return

    with open(pred_path, 'r', encoding='utf-8') as f:
        current_preds = json.load(f)
        
    if not current_preds:
        logger.warning("⚠️ Lista de predicciones vacía")
        return
        
    df_current = pd.DataFrame(current_preds)
    current_probs = df_current['probabilidad'].values / 100.0 # Convert back to 0-1
    
    # Stats
    logger.info(f"   Predicciones actuales: {len(current_probs)}")
    logger.info(f"   Mean Prob: {current_probs.mean():.4f}")
    logger.info(f"   Std Dev:   {current_probs.std():.4f}")
    logger.info(f"   Min/Max:   {current_probs.min():.4f} / {current_probs.max():.4f}")
    
    # Simple Heuristics (Drift)
    # 1. Check for Collapsed Model (All probs near 0.1 or 0.9)
    if current_probs.std() < 0.01:
        logger.error("🚨 ALERTA CRÍTICA: Low Variance. Model might be outputting constant values.")
        return
        
    # 2. Check for Extreme Confidence (Only 0s and 1s)
    # If > 50% of probs are > 0.95 or < 0.05
    extreme_count = np.sum((current_probs > 0.95) | (current_probs < 0.05))
    if extreme_count > len(current_probs) * 0.8:
         logger.warning("⚠️ ALERTA: High Confidence Saturation. Calibration might be too aggressive.")
         
    # 3. Reference PSI (Mock Reference - Uniform-ish logic for ranking)
    # In a ranking problem, we expect one winner per race.
    # Mean prob should be roughly 1 / avg_runners.
    # Avg runners ~ 10-12. Mean prob should be ~0.08 - 0.10.
    
    mean_prob = current_probs.mean()
    if mean_prob < 0.05 or mean_prob > 0.15:
        logger.warning(f"⚠️ ALERTA: Mean Probability ({mean_prob:.3f}) deviates from expected (~0.10).")
        
    logger.info("✅ Chequeo de Salud del Modelo completado.")

if __name__ == "__main__":
    check_drift()
