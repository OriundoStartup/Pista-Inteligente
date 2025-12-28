"""
Entrenamiento del Ensemble GBDT v4.0
Combina LightGBM + XGBoost + CatBoost con Ridge meta-learner

Author: ML Engineering Team
Date: 2025-12-28
"""

import sys
import os
import pandas as pd
import numpy as np
from src.models.data_manager import cargar_datos_3nf
from src.models.features import FeatureEngineering
from src.models.ensemble_ranker import EnsembleRanker, compare_ensemble_vs_baseline
from lightgbm import LGBMRanker
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def prepare_training_data():
    """Prepara datos para entrenamiento"""
    logger.info("Cargando datos históricos...")
    df = cargar_datos_3nf()
    
    if df.empty:
        raise ValueError("No hay datos para entrenar")
    
    logger.info(f"   Datos cargados: {len(df)} registros")
    
    # Feature Engineering
    logger.info("Generando features...")
    fe = FeatureEngineering()
    X = fe.transform(df, is_training=True)
    
    # Target (relevance based on position)
    def get_relevance(pos):
        """
        Convierte posición a relevance score
        Posiciones mejores = scores más altos
        """
        if pd.isna(pos):
            return 0
        pos = int(pos)
        if pos == 1: return 10
        if pos == 2: return 5
        if pos == 3: return 3
        if pos == 4: return 2
        if pos == 5: return 1
        return 0
    
    y = df['posicion'].apply(get_relevance)
    
    # Groups (race IDs - crítico para ranking)
    df['race_id'] = (
        df['hipodromo'].astype(str) + '_' + 
        df['fecha'].astype(str) + '_' + 
        df['nro_carrera'].astype(str)
    )
    groups = df['race_id']
    
    logger.info(f"   Features: {X.shape[1]} columnas")
    logger.info(f"   Carreras únicas: {groups.nunique()}")
    logger.info(f"   Distribución de relevance:")
    for relevance, count in y.value_counts().sort_index(ascending=False).items():
        logger.info(f"      Score {relevance:2d}: {count:5d} samples")
    
    # Categorical features para CatBoost (si existen)
    categorical_cols = []
    for col in ['jinete_id', 'preparador_id', 'hipodromo_id', 'padre']:
        if col in X.columns:
            categorical_cols.append(col)
    
    categorical_features = categorical_cols if categorical_cols else None
    
    if categorical_features:
        logger.info(f"   Features categóricas: {categorical_features}")
    
    return X, y, groups, fe, categorical_features


def train_ensemble():
    """Entrena el ensemble completo"""
    logger.info("\n" + "="*70)
    logger.info("ENTRENAMIENTO ENSEMBLE v4.0")
    logger.info("="*70 + "\n")
    
    # Preparar datos
    X, y, groups, fe, categorical_features = prepare_training_data()
    
    # Split temporal (80/20) - CRÍTICO: mantener orden temporal
    logger.info("\nDividiendo dataset...")
    unique_groups = groups.unique()
    n_groups = len(unique_groups)
    split_idx = int(n_groups * 0.8)
    
    train_groups = unique_groups[:split_idx]
    test_groups = unique_groups[split_idx:]
    
    train_mask = groups.isin(train_groups)
    test_mask = groups.isin(test_groups)
    
    X_train, X_test = X[train_mask], X[test_mask]
    y_train, y_test = y[train_mask], y[test_mask]
    groups_train, groups_test = groups[train_mask], groups[test_mask]
    
    logger.info(f"   Train: {len(X_train):,} samples, {len(train_groups):,} carreras")
    logger.info(f"   Test:  {len(X_test):,} samples, {len(test_groups):,} carreras")
    
    # Entrenar Ensemble
    logger.info("\n" + "="*70)
    logger.info("INICIANDO ENTRENAMIENTO DEL ENSEMBLE")
    logger.info("="*70)
    
    ensemble = EnsembleRanker(save_individual_models=True)
    ensemble.fit(X_train, y_train, groups_train, categorical_features)
    
    # Entrenar baseline para comparación
    logger.info("\n" + "="*70)
    logger.info("ENTRENANDO BASELINE LIGHTGBM PARA COMPARACIÓN")
    logger.info("="*70)
    
    lgbm_baseline = LGBMRanker(
        objective='lambdarank',
        metric='ndcg',
        n_estimators=500,
        learning_rate=0.05,
        random_state=42,
        n_jobs=-1,
        verbose=-1
    )
    
    train_group_counts = groups_train.value_counts().sort_index().values
    lgbm_baseline.fit(X_train, y_train, group=train_group_counts)
    
    logger.info("✅ Baseline entrenado")
    
    # Comparar en test set
    logger.info("\n" + "="*70)
    logger.info("EVALUACIÓN EN TEST SET")
    logger.info("="*70)
    
    results = compare_ensemble_vs_baseline(
        X_test, y_test, groups_test,
        ensemble, lgbm_baseline
    )
    
    # Guardar modelos
    logger.info("\n" + "="*70)
    logger.info("GUARDANDO MODELOS")
    logger.info("="*70)
    
    # Guardar ensemble (crea automáticamente alias 'latest')
    ensemble_path = ensemble.save('src/models/ensemble')
    
    # Guardar Feature Engineering con versionado
    import joblib
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    fe.save(f'src/models/feature_eng_v4_ensemble_{timestamp}.pkl')
    fe.save('src/models/feature_eng_v4_ensemble.pkl')  # Latest alias
    logger.info(f"✅ Feature Engineering guardado: src/models/feature_eng_v4_ensemble.pkl")
    
    # Guardar metadatos del entrenamiento
    metadata = {
        'version': '4.0',
        'timestamp': timestamp,
        'ensemble_ndcg': float(results['ensemble_ndcg']),
        'baseline_ndcg': float(results['baseline_ndcg']),
        'mejora_porcentual': float(results['mejora_porcentual']),
        'ensemble_mejor': bool(results['ensemble_mejor']),
        'n_features': int(X.shape[1]),
        'n_samples_train': int(len(X_train)),
        'n_samples_test': int(len(X_test)),
        'n_races_train': int(len(train_groups)),
        'n_races_test': int(len(test_groups))
    }
    
    import json
    metadata_path = 'src/models/ensemble_metadata.json'
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"✅ Metadatos guardados: {metadata_path}")
    
    # Guardar también baseline para referencia
    baseline_path = 'src/models/lgbm_baseline_for_comparison.pkl'
    joblib.dump(lgbm_baseline, baseline_path)
    logger.info(f"✅ Baseline guardado: {baseline_path}")
    
    # Resumen final
    logger.info("\n" + "="*70)
    logger.info("✅ ENTRENAMIENTO COMPLETADO EXITOSAMENTE")
    logger.info("="*70)
    logger.info(f"\n📁 Archivos generados:")
    logger.info(f"   - Ensemble: {ensemble_path}")
    logger.info(f"   - Feature Engineering: src/models/feature_eng_v4_ensemble.pkl")
    logger.info(f"   - Baseline: {baseline_path}")
    
    logger.info(f"\n📊 Performance:")
    logger.info(f"   - Ensemble NDCG: {results['ensemble_ndcg']:.4f}")
    logger.info(f"   - Baseline NDCG: {results['baseline_ndcg']:.4f}")
    logger.info(f"   - Mejora: {results['mejora_porcentual']:+.2f}%")
    
    if results['ensemble_mejor']:
        logger.info(f"\n🏆 EL ENSEMBLE SUPERA AL BASELINE!")
    else:
        logger.info(f"\n⚠️  El baseline tiene mejor performance (puede ser varianza)")
    
    logger.info(f"\n💡 Próximo paso:")
    logger.info(f"   Integrar ensemble en inference pipeline")
    logger.info(f"   Ejecutar: python -m src.models.inference_ensemble")
    
    return ensemble, results


if __name__ == "__main__":
    try:
        ensemble, results = train_ensemble()
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Error en entrenamiento: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
