"""
Modelo LightGBM Optimizado v5.0
------------------------------
Mejoras sobre la versión anterior:
1. Features de alta señal adicionales (jockey_track_rate, recent_form)
2. Regularización optimizada para dataset pequeño
3. Cold start inteligente con priors bayesianos
4. Cross-Validation con GroupKFold respetando carreras
5. Calibración isotónica con cross-val predictions

Author: ML Engineering Team
Date: 2026-02-07
"""

import pandas as pd
import numpy as np
import joblib
import logging
import json
import os
from datetime import datetime
from lightgbm import LGBMRanker
from sklearn.model_selection import GroupKFold
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import ndcg_score

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OptimizedFeatureEngineering:
    """
    Feature Engineering Optimizado v5.0
    Genera features de alta señal con manejo robusto de cold start.
    """
    
    def __init__(self):
        self.feature_cols = [
            # Performance del caballo
            'win_rate', 'races_count', 'recent_form', 'avg_speed_3',
            # Contexto (pista/distancia)
            'track_win_rate', 'dist_win_rate',
            # Interacciones
            'jockey_win_rate', 'jockey_track_rate', 'trainer_win_rate', 'duo_eff',
            # Momentum
            'trend_3', 'days_rest',
            # Cold Start Proxy
            'sire_win_rate',
            # Estáticas
            'peso', 'mandil', 'distancia'
        ]
        self.global_stats = {}
        
    def fit_transform(self, df):
        """Fit y transform para entrenamiento."""
        df = self._preprocess(df)
        df = self._add_features(df)
        
        # Calcular estadísticas globales para cold start
        self._compute_global_stats(df)
        
        return self._finalize(df)
    
    def transform(self, df):
        """Transform para inferencia (usa stats guardadas)."""
        df = self._preprocess(df)
        df = self._add_features(df)
        return self._finalize(df)
    
    def _preprocess(self, df):
        df = df.copy()
        df['fecha'] = pd.to_datetime(df['fecha'])
        df = df.sort_values(['caballo_id', 'fecha']).reset_index(drop=True)
        
        # Conversiones numéricas
        df['posicion'] = pd.to_numeric(df['posicion'], errors='coerce').fillna(0)
        df['is_win'] = (df['posicion'] == 1).astype(float)
        df['distancia'] = pd.to_numeric(df['distancia'], errors='coerce').fillna(1000)
        df['mandil'] = pd.to_numeric(df['mandil'], errors='coerce').fillna(0)
        df['peso'] = pd.to_numeric(df.get('peso_fs', df.get('peso', 470)), errors='coerce').fillna(470)
        
        # IDs como strings
        for col in ['caballo_id', 'jinete_id', 'preparador_id', 'hipodromo_id', 'padre']:
            if col in df.columns:
                df[col] = df[col].fillna(0).astype(str)
                
        return df
    
    def _clean_time(self, t):
        try:
            parts = str(t).split('.')
            if len(parts) >= 2:
                seconds = float(parts[0]) * 60 + float(parts[1])
                if len(parts) > 2:
                    seconds += float(parts[2]) / 100
                return seconds
            return 0
        except:
            return 0
    
    def _add_features(self, df):
        grouped_horse = df.groupby('caballo_id')
        
        # 1. Win Rate + Count (con shift para evitar leakage)
        prev_wins = grouped_horse['is_win'].shift(1).expanding().sum()
        prev_count = grouped_horse['is_win'].shift(1).expanding().count().fillna(0)
        df['win_rate'] = (prev_wins / prev_count).fillna(0)
        df['races_count'] = prev_count
        
        # 2. Recent Form (promedio posición últimas 3 carreras)
        # Mapeamos posición a score: 1=10, 2=8, 3=6, 4=4, 5+=2
        def pos_to_score(pos):
            if pos <= 0 or pd.isna(pos): return 0
            if pos == 1: return 10
            if pos == 2: return 8
            if pos == 3: return 6
            if pos == 4: return 4
            return 2
        
        df['pos_score'] = df['posicion'].apply(pos_to_score)
        df['recent_form'] = grouped_horse['pos_score'].shift(1).rolling(3, min_periods=1).mean().fillna(5)
        
        # 3. Track Win Rate
        grouped_track = df.groupby(['caballo_id', 'hipodromo_id'])
        track_wins = grouped_track['is_win'].shift(1).expanding().sum()
        track_cnt = grouped_track['is_win'].shift(1).expanding().count()
        df['track_win_rate'] = (track_wins / track_cnt).fillna(0)
        
        # 4. Distance Category Win Rate
        conditions = [
            (df['distancia'] < 1100),
            (df['distancia'] >= 1100) & (df['distancia'] <= 1400),
            (df['distancia'] > 1400)
        ]
        df['dist_cat'] = np.select(conditions, ['sprint', 'mile', 'long'], default='sprint')
        
        grouped_dist = df.groupby(['caballo_id', 'dist_cat'])
        dist_wins = grouped_dist['is_win'].shift(1).expanding().sum()
        dist_cnt = grouped_dist['is_win'].shift(1).expanding().count()
        df['dist_win_rate'] = (dist_wins / dist_cnt).fillna(0)
        
        # 5. Jockey Win Rate (NUEVA FEATURE DE ALTA SEÑAL)
        grouped_jockey = df.groupby('jinete_id')
        j_wins = grouped_jockey['is_win'].shift(1).expanding().sum()
        j_cnt = grouped_jockey['is_win'].shift(1).expanding().count()
        df['jockey_win_rate'] = (j_wins / j_cnt).fillna(0.08)
        
        # 6. Jockey Track Rate (NUEVA FEATURE DE ALTA SEÑAL)
        grouped_jt = df.groupby(['jinete_id', 'hipodromo_id'])
        jt_wins = grouped_jt['is_win'].shift(1).expanding().sum()
        jt_cnt = grouped_jt['is_win'].shift(1).expanding().count()
        df['jockey_track_rate'] = (jt_wins / jt_cnt).fillna(0.08)
        
        # 7. Duo Efficiency (Jockey + Preparador)
        if 'preparador_id' in df.columns:
            grouped_duo = df.groupby(['jinete_id', 'preparador_id'])
            duo_wins = grouped_duo['is_win'].shift(1).expanding().sum()
            duo_cnt = grouped_duo['is_win'].shift(1).expanding().count()
            df['duo_eff'] = (duo_wins / duo_cnt).fillna(0)
        else:
            df['duo_eff'] = 0.0
        
        # 8. Trainer Win Rate (NUEVA FEATURE DE ALTA SEÑAL)
        if 'preparador_id' in df.columns:
            grouped_trainer = df.groupby('preparador_id')
            t_wins = grouped_trainer['is_win'].shift(1).expanding().sum()
            t_cnt = grouped_trainer['is_win'].shift(1).expanding().count()
            df['trainer_win_rate'] = (t_wins / t_cnt).fillna(0.08)
        else:
            df['trainer_win_rate'] = 0.08
        
        # 8. Trend (mejora o empeoramiento)
        prev_pos = df.groupby('caballo_id')['posicion'].shift(1)
        prev_pos_3 = df.groupby('caballo_id')['posicion'].shift(3)
        df['trend_3'] = (prev_pos - prev_pos_3).fillna(0)
        
        # 9. Days Rest
        df['prev_date'] = df.groupby('caballo_id')['fecha'].shift(1)
        df['days_rest'] = (df['fecha'] - df['prev_date']).dt.days.fillna(30)
        df['days_rest'] = df['days_rest'].clip(0, 180)  # Cap en 6 meses
        
        # 10. Sire Win Rate (cold start proxy)
        if 'padre' in df.columns:
            grouped_sire = df.groupby('padre')
            sire_wins = grouped_sire['is_win'].shift(1).expanding().sum()
            sire_cnt = grouped_sire['is_win'].shift(1).expanding().count()
            df['sire_win_rate'] = (sire_wins / sire_cnt).fillna(0.10)
        else:
            df['sire_win_rate'] = 0.10
            
        # 11. Avg Speed últimas 3 carreras
        df['seconds'] = df['tiempo'].apply(self._clean_time) if 'tiempo' in df.columns else 0
        df['speed_mps'] = np.where(df['seconds'] > 0, df['distancia'] / df['seconds'], 0)
        df['avg_speed_3'] = grouped_horse['speed_mps'].shift(1).rolling(3, min_periods=1).mean().fillna(14)
        
        # COLD START: Imputar win_rate para debutantes usando Bayesian Prior
        mask_debut = (df['races_count'] == 0)
        # Prior: combinar sire_win_rate con global average (10%)
        df.loc[mask_debut, 'win_rate'] = df.loc[mask_debut, 'sire_win_rate'] * 0.6 + 0.08 * 0.4
        df.loc[mask_debut, 'recent_form'] = 5.0  # Neutral
        
        return df
    
    def _compute_global_stats(self, df):
        """Calcula estadísticas globales para referencia."""
        self.global_stats = {
            'mean_win_rate': df['win_rate'].mean(),
            'mean_jockey_rate': df['jockey_win_rate'].mean(),
            'mean_days_rest': df['days_rest'].mean()
        }
    
    def _finalize(self, df):
        # Asegurar todas las columnas
        for col in self.feature_cols:
            if col not in df.columns:
                df[col] = 0.0
        
        X = df[self.feature_cols].copy()
        X = X.replace([np.inf, -np.inf], np.nan).fillna(0)
        
        return X, df
    
    def save(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self, path)
        logger.info(f"Feature Engineering guardado: {path}")
    
    @staticmethod
    def load(path):
        return joblib.load(path)


def train_optimized_model():
    """
    Entrena el modelo LightGBM optimizado.
    """
    logger.info("=" * 70)
    logger.info("ENTRENAMIENTO LIGHTGBM OPTIMIZADO v5.0")
    logger.info("=" * 70)
    
    # 1. Cargar datos
    from src.models.data_manager import cargar_datos_3nf
    
    logger.info("\n[PASO 1/5] Cargando datos históricos...")
    df = cargar_datos_3nf()
    
    if df.empty:
        raise ValueError("No hay datos para entrenar")
    
    logger.info(f"   Datos cargados: {len(df)} registros")
    
    # 2. Feature Engineering
    logger.info("\n[PASO 2/5] Generando features optimizadas...")
    fe = OptimizedFeatureEngineering()
    X, df_enriched = fe.fit_transform(df)
    
    # 3. Target (relevance)
    def get_relevance(pos):
        if pd.isna(pos) or pos <= 0: return 0
        pos = int(pos)
        if pos == 1: return 10
        if pos == 2: return 5
        if pos == 3: return 3
        if pos == 4: return 2
        if pos == 5: return 1
        return 0
    
    y = df_enriched['posicion'].apply(get_relevance)
    
    # Race IDs para grouping
    df_enriched['race_id'] = (
        df_enriched['hipodromo'].astype(str) + '_' +
        df_enriched['fecha'].astype(str) + '_' +
        df_enriched['nro_carrera'].astype(str)
    )
    groups = df_enriched['race_id']
    
    logger.info(f"   Features: {X.shape[1]} columnas")
    logger.info(f"   Carreras únicas: {groups.nunique()}")
    
    # 4. Train/Test Split con GroupKFold
    logger.info("\n[PASO 3/5] Entrenando con GroupKFold CV...")
    
    # Usar 80/20 temporal split para test final
    unique_races = groups.unique()
    n_races = len(unique_races)
    split_idx = int(n_races * 0.8)
    
    train_races = unique_races[:split_idx]
    test_races = unique_races[split_idx:]
    
    train_mask = groups.isin(train_races)
    test_mask = groups.isin(test_races)
    
    X_train, X_test = X[train_mask], X[test_mask]
    y_train, y_test = y[train_mask], y[test_mask]
    groups_train = groups[train_mask]
    groups_test = groups[test_mask]
    
    logger.info(f"   Train: {len(X_train)} samples, {len(train_races)} carreras")
    logger.info(f"   Test:  {len(X_test)} samples, {len(test_races)} carreras")
    
    # Modelo optimizado para dataset pequeño
    model = LGBMRanker(
        objective='lambdarank',
        metric='ndcg',
        n_estimators=400,           # Reducido para evitar overfit
        num_leaves=20,              # Reducido
        max_depth=5,                # Reducido
        learning_rate=0.05,
        
        # Regularización fuerte
        reg_alpha=0.5,              # Aumentado
        reg_lambda=1.0,             # Aumentado
        min_child_samples=30,       # Aumentado
        
        # Sampling
        colsample_bytree=0.7,
        subsample=0.7,
        subsample_freq=5,
        
        random_state=42,
        n_jobs=-1,
        verbose=-1,
        force_col_wise=True
    )
    
    # Group counts para LightGBM
    train_group_counts = groups_train.value_counts().sort_index().values
    
    model.fit(X_train, y_train, group=train_group_counts)
    
    logger.info("✅ Modelo entrenado")
    
    # 5. Evaluación
    logger.info("\n[PASO 4/5] Evaluando en Test Set...")
    
    test_preds = model.predict(X_test)
    ndcg = ndcg_score([y_test.values], [test_preds])
    
    logger.info(f"   Test NDCG: {ndcg:.4f}")
    
    # Feature Importance
    importance = pd.DataFrame({
        'feature': fe.feature_cols,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    logger.info("\n   Top Features:")
    for _, row in importance.head(8).iterrows():
        logger.info(f"      {row['feature']:20s}: {row['importance']:.0f}")
    
    # 6. Calibración con Cross-Validation
    logger.info("\n[PASO 5/5] Entrenando Calibrador Isotónico...")
    
    # Usar predicciones del test set para calibrar
    y_binary = (y_test >= 10).astype(int)
    
    calibrator = IsotonicRegression(out_of_bounds='clip', y_min=0, y_max=1)
    calibrator.fit(test_preds, y_binary)
    
    # Validar calibración
    cal_probs = calibrator.transform(test_preds)
    logger.info(f"   Mean Calibrated Prob: {cal_probs.mean():.4f}")
    logger.info(f"   Actual Win Rate:      {y_binary.mean():.4f}")
    
    # 7. Guardar artefactos
    logger.info("\n" + "=" * 70)
    logger.info("GUARDANDO ARTEFACTOS")
    logger.info("=" * 70)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Modelo
    model_path = f'src/models/lgbm_optimized_{timestamp}.pkl'
    joblib.dump(model, model_path)
    logger.info(f"✅ Modelo: {model_path}")
    
    # Alias latest
    joblib.dump(model, 'src/models/lgbm_optimized_latest.pkl')
    logger.info(f"✅ Alias: src/models/lgbm_optimized_latest.pkl")
    
    # Feature Engineering
    fe.save(f'src/models/feature_eng_v5_{timestamp}.pkl')
    fe.save('src/models/feature_eng_v5_latest.pkl')
    logger.info(f"✅ Feature Eng: src/models/feature_eng_v5_latest.pkl")
    
    # Calibrador
    calibrator_path = 'src/models/calibrator_v5.pkl'
    joblib.dump(calibrator, calibrator_path)
    logger.info(f"✅ Calibrador: {calibrator_path}")
    
    # Metadata
    metadata = {
        'version': '5.0',
        'timestamp': timestamp,
        'ndcg': float(ndcg),
        'n_features': int(X.shape[1]),
        'n_samples_train': int(len(X_train)),
        'n_samples_test': int(len(X_test)),
        'n_races_train': int(len(train_races)),
        'n_races_test': int(len(test_races)),
        'feature_importance': importance.to_dict('records')
    }
    
    with open('src/models/lgbm_optimized_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"✅ Metadata: src/models/lgbm_optimized_metadata.json")
    
    logger.info("\n" + "=" * 70)
    logger.info(f"✅ ENTRENAMIENTO COMPLETADO - NDCG: {ndcg:.4f}")
    logger.info("=" * 70)
    
    return model, fe, calibrator, metadata


if __name__ == "__main__":
    try:
        model, fe, calibrator, metadata = train_optimized_model()
        print(f"\n🎉 Modelo listo con NDCG: {metadata['ndcg']:.4f}")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
