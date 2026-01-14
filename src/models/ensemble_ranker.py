"""
Ensemble de 3 GBDT con Meta-Learner Ridge
Combina LightGBM, XGBoost y CatBoost para predicciones superiores

Author: ML Engineering Team
Date: 2025-12-28
Version: 4.0
"""

import numpy as np
import pandas as pd
from lightgbm import LGBMRanker
from xgboost import XGBRanker
from catboost import CatBoostRanker
from sklearn.linear_model import Ridge
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import ndcg_score
import joblib
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnsembleRanker:
    """
    Ensemble de 3 modelos GBDT con stacking
    
    Arquitectura:
    - Base models: LightGBM, XGBoost, CatBoost
    - Meta-learner: Ridge regression
    - Strategy: Stacking con out-of-fold predictions
    
    Example:
        >>> ensemble = EnsembleRanker()
        >>> ensemble.fit(X_train, y_train, groups_train)
        >>> predictions = ensemble.predict(X_test)
    """
    
    def __init__(self, save_individual_models=True):
        """
        Args:
            save_individual_models: Si se guardan los modelos base individualmente
        """
        self.save_individual_models = save_individual_models
        
        # Base Models (configuración optimizada)
        self.lgbm = self._build_lgbm()
        self.xgb = self._build_xgb()
        self.catboost = self._build_catboost()
        
        # Meta-learner
        self.meta_model = Ridge(alpha=1.0, random_state=42)
        
        # Model names
        self.base_model_names = ['LightGBM', 'XGBoost', 'CatBoost']
        self.base_models = [self.lgbm, self.xgb, self.catboost]
        
        # OOF predictions (para análisis)
        self.oof_predictions = None
        self.meta_weights = None
    
    def _build_lgbm(self):
        """LightGBM con configuración optimizada"""
        return LGBMRanker(
            objective='lambdarank',
            metric='ndcg',
            n_estimators=800,
            num_leaves=31,
            max_depth=8,
            learning_rate=0.03,
            
            # Regularización
            reg_alpha=0.1,
            reg_lambda=0.2,
            min_child_samples=20,
            
            # Sampling
            colsample_bytree=0.8,
            subsample=0.8,
            subsample_freq=5,
            
            random_state=42,
            n_jobs=-1,
            verbose=-1,
            force_col_wise=True
        )
    
    def _build_xgb(self):
        """XGBoost con configuración optimizada"""
        return XGBRanker(
            objective='rank:ndcg',
            n_estimators=1000,
            max_depth=6,
            learning_rate=0.02,
            
            # Regularización fuerte
            gamma=0.1,
            reg_alpha=0.5,
            reg_lambda=1.0,
            min_child_weight=5,
            
            # Sampling
            colsample_bytree=0.7,
            subsample=0.8,
            
            tree_method='hist',
            random_state=42,
            n_jobs=-1,
            verbosity=0
        )
    
    def _build_catboost(self):
        """CatBoost con configuración optimizada"""
        return CatBoostRanker(
            loss_function='YetiRank',
            iterations=800,
            depth=6,
            learning_rate=0.03,
            l2_leaf_reg=3.0,
            
            random_seed=42,
            verbose=False,
            allow_writing_files=False
        )
    
    def fit(self, X, y, groups, categorical_features=None):
        """
        Entrena el ensemble con stacking
        
        Args:
            X: Features (DataFrame)
            y: Target (relevance scores)
            groups: Group IDs para ranking (race IDs)
            categorical_features: Lista de columnas categóricas para CatBoost
        
        Returns:
            self
        """
        logger.info("="*70)
        logger.info("ENTRENANDO ENSEMBLE DE 3 GBDT + META-LEARNER")
        logger.info("="*70)
        
        # Preparar datos
        X_np = X.values if isinstance(X, pd.DataFrame) else X
        y_np = y.values if isinstance(y, pd.Series) else y
        groups_np = groups.values if isinstance(groups, pd.Series) else groups
        
        # Paso 1: Generar out-of-fold predictions para meta-learner
        logger.info("\n[PASO 1/3] Generando OOF predictions con CV temporal...")
        oof_preds = self._generate_oof_predictions(
            X, y, groups, categorical_features
        )
        
        # Paso 2: Entrenar meta-learner
        logger.info("\n[PASO 2/3] Entrenando meta-learner Ridge...")
        self.meta_model.fit(oof_preds, y_np)
        
        # Guardar coeficientes
        self.meta_weights = {
            name: coef 
            for name, coef in zip(self.base_model_names, self.meta_model.coef_)
        }
        
        logger.info(f"\n✅ Meta-learner entrenado")
        logger.info(f"   Pesos aprendidos:")
        for name, weight in self.meta_weights.items():
            logger.info(f"      {name:12s}: {weight:.4f}")
        
        # Paso 3: Re-entrenar base models en TODO el dataset
        logger.info("\n[PASO 3/3] Re-entrenando base models en dataset completo...")
        self._retrain_base_models(X, y, groups, categorical_features)
        
        logger.info("\n" + "="*70)
        logger.info("✅ ENSEMBLE ENTRENADO EXITOSAMENTE")
        logger.info("="*70)
        
        return self
    
    def _generate_oof_predictions(self, X, y, groups, categorical_features=None):
        """
        Genera out-of-fold predictions usando CV temporal
        
        Esto evita overfitting del meta-learner
        """
        n_splits = 5
        tscv = TimeSeriesSplit(n_splits=n_splits)
        
        # Preparar array para OOF predictions
        n_samples = len(X)
        n_models = len(self.base_models)
        oof_preds = np.zeros((n_samples, n_models))
        
        logger.info(f"   Cross-Validation: {n_splits} folds temporales")
        
        # CV por cada modelo
        for model_idx, (model, name) in enumerate(zip(self.base_models, self.base_model_names)):
            logger.info(f"\n   Modelo {model_idx + 1}/3: {name}")
            
            # Time series split
            fold_scores = []
            
            for fold, (train_idx, val_idx) in enumerate(tscv.split(X), 1):
                # Split data
                X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
                y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
                g_train, g_val = groups.iloc[train_idx], groups.iloc[val_idx]
                
                # Get group counts
                train_groups = g_train.value_counts().sort_index().values
                val_groups = g_val.value_counts().sort_index().values
                
                # Train
                if isinstance(model, CatBoostRanker):
                    model.fit(
                        X_train, y_train, group_id=g_train,
                        cat_features=categorical_features,
                        verbose=False
                    )
                else:
                    model.fit(X_train, y_train, group=train_groups)
                
                # Predict on validation (OOF)
                val_preds = model.predict(X_val)
                oof_preds[val_idx, model_idx] = val_preds
                
                # Evaluate
                score = ndcg_score([y_val.values], [val_preds])
                fold_scores.append(score)
                
                logger.info(f"      Fold {fold}/{n_splits}: NDCG = {score:.4f}")
            
            avg_score = np.mean(fold_scores)
            std_score = np.std(fold_scores)
            logger.info(f"      {name} CV Score: {avg_score:.4f} ± {std_score:.4f}")
        
        self.oof_predictions = oof_preds
        return oof_preds
    
    def _retrain_base_models(self, X, y, groups, categorical_features=None):
        """Re-entrena base models en todo el dataset"""
        # Get group counts
        group_counts = groups.value_counts().sort_index().values
        
        for model, name in zip(self.base_models, self.base_model_names):
            logger.info(f"   Re-entrenando {name}...")
            
            if isinstance(model, CatBoostRanker):
                model.fit(
                    X, y, group_id=groups,
                    cat_features=categorical_features,
                    verbose=False
                )
            else:
                model.fit(X, y, group=group_counts)
            
            logger.info(f"      ✅ {name} entrenado")
    
    def predict(self, X):
        """
        Genera predicciones del ensemble
        
        Args:
            X: Features
        
        Returns:
            Final scores (numpy array)
        """
        # Predicciones de base models
        base_preds = np.column_stack([
            model.predict(X) for model in self.base_models
        ])
        
        # Meta-learner combina
        final_scores = self.meta_model.predict(base_preds)
        
        return final_scores
    
    def predict_with_details(self, X):
        """
        Predicción con detalles de cada modelo
        
        Returns:
            dict con 'final_scores', 'lgbm_scores', 'xgb_scores', 'catboost_scores'
        """
        base_preds = {}
        for model, name in zip(self.base_models, self.base_model_names):
            base_preds[f'{name.lower()}_scores'] = model.predict(X)
        
        # Stack
        stacked = np.column_stack(list(base_preds.values()))
        
        # Final
        base_preds['final_scores'] = self.meta_model.predict(stacked)
        
        return base_preds
    
    def save(self, path_prefix='src/models/ensemble'):
        """
        Guarda el ensemble completo
        
        Args:
            path_prefix: Prefijo de ruta (sin extensión)
        """
        import os
        os.makedirs(os.path.dirname(path_prefix), exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save ensemble completo
        ensemble_data = {
            'lgbm': self.lgbm,
            'xgb': self.xgb,
            'catboost': self.catboost,
            'meta_model': self.meta_model,
            'meta_weights': self.meta_weights,
            'timestamp': timestamp
        }
        
        ensemble_path = f'{path_prefix}_{timestamp}.pkl'
        joblib.dump(ensemble_data, ensemble_path)
        logger.info(f"✅ Ensemble guardado: {ensemble_path}")
        
        # Crear alias "latest"
        latest_path = f'{path_prefix}_latest.pkl'
        joblib.dump(ensemble_data, latest_path)
        logger.info(f"✅ Alias latest: {latest_path}")
        
        # Guardar modelos individuales si se requiere
        if self.save_individual_models:
            for model, name in zip(self.base_models, self.base_model_names):
                model_path = f'{path_prefix}_{name.lower()}_{timestamp}.pkl'
                joblib.dump(model, model_path)
        
        return ensemble_path
    
    @classmethod
    def load(cls, path='src/models/ensemble_latest.pkl'):
        """
        Carga ensemble guardado
        
        Args:
            path: Ruta al archivo
        
        Returns:
            EnsembleRanker instance
        """
        data = joblib.load(path)
        
        # Crear instancia
        ensemble = cls(save_individual_models=False)
        
        # Restaurar modelos
        ensemble.lgbm = data['lgbm']
        ensemble.xgb = data['xgb']
        ensemble.catboost = data['catboost']
        ensemble.meta_model = data['meta_model']
        ensemble.meta_weights = data['meta_weights']
        
        # Update base_models list
        ensemble.base_models = [ensemble.lgbm, ensemble.xgb, ensemble.catboost]
        
        logger.info(f"✅ Ensemble cargado desde: {path}")
        logger.info(f"   Timestamp: {data.get('timestamp', 'N/A')}")
        logger.info(f"   Pesos:")
        for name, weight in ensemble.meta_weights.items():
            logger.info(f"      {name:12s}: {weight:.4f}")
        
        return ensemble


def compare_ensemble_vs_baseline(X_test, y_test, groups_test, 
                                   ensemble, lgbm_baseline):
    """
    Compara ensemble vs baseline LightGBM
    
    Returns:
        dict con métricas comparativas
    """
    # Predicciones
    ensemble_preds = ensemble.predict(X_test)
    baseline_preds = lgbm_baseline.predict(X_test)
    
    # Métricas
    ensemble_ndcg = ndcg_score([y_test.values], [ensemble_preds])
    baseline_ndcg = ndcg_score([y_test.values], [baseline_preds])
    
    mejora = (ensemble_ndcg - baseline_ndcg) / baseline_ndcg * 100
    
    results = {
        'ensemble_ndcg': ensemble_ndcg,
        'baseline_ndcg': baseline_ndcg,
        'mejora_porcentual': mejora,
        'ensemble_mejor': ensemble_ndcg > baseline_ndcg
    }
    
    logger.info("\n" + "="*70)
    logger.info("COMPARACIÓN: ENSEMBLE VS BASELINE")
    logger.info("="*70)
    logger.info(f"Ensemble NDCG:  {ensemble_ndcg:.4f}")
    logger.info(f"Baseline NDCG:  {baseline_ndcg:.4f}")
    logger.info(f"Mejora:         {mejora:+.2f}%")
    logger.info(f"Ganador:        {'🏆 ENSEMBLE' if results['ensemble_mejor'] else 'BASELINE'}")
    logger.info("="*70)
    
    return results
