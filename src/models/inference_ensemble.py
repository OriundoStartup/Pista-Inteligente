"""
Pipeline de Inferencia para Ensemble v4
Usa EnsembleRanker (LightGBM + XGBoost + CatBoost) para predicciones

Author: ML Engineering Team
Date: 2025-12-28
Version: 4.0
"""

import pandas as pd
import numpy as np
import os
import json
import sys
import logging
import time
import gc
from datetime import datetime
from src.models.data_manager import cargar_programa, cargar_datos_3nf
from src.models.features import FeatureEngineering
from src.models.ensemble_ranker import EnsembleRanker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Fix for Windows Unicode printing
if sys.platform == "win32" and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


class EnsembleInferencePipeline:
    """Pipeline de inferencia usando Ensemble v4"""
    
    def __init__(self, 
                 ensemble_path='src/models/ensemble_latest.pkl',
                 fe_path='src/models/feature_eng_v4_ensemble.pkl'):
        """
        Args:
            ensemble_path: Ruta al ensemble guardado
            fe_path: Ruta al feature engineering
        """
        self.ensemble_path = ensemble_path
        self.fe_path = fe_path
        self.ensemble = None
        self.fe = None
        self.history = None
        
        # 🎯 Professional Probability Calibration
        # Temperature: Lower = more confident (larger differences)
        # Amplification: Higher = amplify score differences
        self.temperature = 0.65  # Slightly more confident than v2
        self.amplification_power = 1.6  # Better separation for ensemble
        
    def load_artifacts(self):
        """Carga modelos y feature engineering"""
        # Verificar existencia de archivos
        if not os.path.exists(self.ensemble_path):
            raise FileNotFoundError(f"Ensemble not found: {self.ensemble_path}")
        
        # Fallback a feature engineering v2 si v4 no existe
        if not os.path.exists(self.fe_path):
            logger.warning(f"FE v4 not found, trying v2 fallback...")
            self.fe_path = 'src/models/feature_eng_v2.pkl'
            if not os.path.exists(self.fe_path):
                raise FileNotFoundError("No feature engineering found")
        
        start = time.time()
        
        # Cargar ensemble
        self.ensemble = EnsembleRanker.load(self.ensemble_path)
        
        # Cargar Feature Engineering
        self.fe = FeatureEngineering.load(self.fe_path)
        
        logger.info("Artifacts loaded", extra={
            'ensemble_path': self.ensemble_path,
            'fe_path': self.fe_path,
            'load_time_ms': int((time.time() - start) * 1000)
        })
        
        # Load History for Feature Generation
        logger.info("Loading historical data for features...")
        self.history = cargar_datos_3nf()
        logger.info(f"✅ History loaded: {len(self.history):,} records")
        
    def run(self):
        """Ejecuta el pipeline completo de inferencia"""
        start_time = time.time()
        logger.info("="*70)
        logger.info("ENSEMBLE V4 INFERENCE PIPELINE")
        logger.info("="*70)
        logger.info(f"Ensemble: {self.ensemble_path}")
        logger.info(f"FE: {self.fe_path}")
        logger.info("="*70)
        
        try:
            # 1. Load artifacts
            self.load_artifacts()
            
            # 2. Load Future Races
            logger.info("\n[PASO 1/4] Cargando programa de carreras futuras...")
            df_program = cargar_programa(solo_futuras=True)
            
            if df_program.empty:
                logger.warning("⚠️ No hay carreras futuras en la base de datos")
                logger.info("El sistema está actualizado. No hay predicciones pendientes.")
                return
            
            logger.info(f"✅ Cargadas {len(df_program)} entradas de programa futuro")
            logger.info(f"   Carreras únicas: {df_program['nro_carrera'].nunique()}")
            logger.info(f"   Fechas: {sorted(df_program['fecha'].unique())}")
            
            # 3. Transform features
            logger.info("\n[PASO 2/4] Transformando features...")
            X_future, df_program_enriched = self._prepare_features(df_program)
            
            # 4. Predict
            logger.info("\n[PASO 3/4] Generando predicciones con Ensemble...")
            predictions = self._predict_with_calibration(X_future, df_program_enriched)
            
            # 5. Save results
            logger.info("\n[PASO 4/4] Guardando resultados...")
            self.save_results(predictions)
            
            # Summary
            elapsed = time.time() - start_time
            logger.info("\n" + "="*70)
            logger.info(f"✅ INFERENCIA COMPLETADA en {elapsed:.2f}s")
            logger.info(f"   Predicciones generadas: {len(predictions)}")
            logger.info(f"   Carreras procesadas: {len(predictions) // max(1, len(df_program) // df_program['nro_carrera'].nunique())}")
            logger.info("="*70)
            
            # Clean up
            gc.collect()
            
        except Exception as e:
            logger.error(f"❌ Error en pipeline de inferencia: {e}", exc_info=True)
            raise
    
    def _prepare_features(self, df_program):
        """
        Prepara features para inferencia
        
        Returns:
            X_future: Features transformadas
            df_program_enriched: Programa enriquecido con IDs mapeados
        """
        # Build ID mappers from history
        caballo_map = self.history[['caballo_id', 'caballo']].drop_duplicates('caballo').set_index('caballo')['caballo_id'].to_dict()
        jinete_map = self.history[['jinete_id', 'jinete']].drop_duplicates('jinete').set_index('jinete')['jinete_id'].to_dict()
        
        # Stud as Preparador
        if 'stud_id' in self.history.columns:
            stud_map = self.history[['stud_id', 'stud']].drop_duplicates('stud').set_index('stud')['stud_id'].to_dict()
        else:
            stud_map = {}
        
        # Create race IDs for grouping
        df_program['race_unique_id'] = (
            df_program['fecha'].astype(str) + "_" + 
            df_program['hipodromo'] + "_" + 
            df_program['nro_carrera'].astype(str)
        )
        
        logger.info(f"   Mapping names to IDs...")
        mapped_rows = []
        
        for idx, row in df_program.iterrows():
            # Get names
            c_name = row.get('caballo', 'Unknown')
            j_name = row.get('jinete', 'Unknown')
            s_name = row.get('stud', 'Unknown')
            
            # Map to IDs (0 for cold start)
            c_id = caballo_map.get(c_name, 0)
            j_id = jinete_map.get(j_name, 0)
            p_id = stud_map.get(s_name, 0)
            
            # Construct input row
            input_row = {
                'fecha': pd.to_datetime(row['fecha']),
                'caballo_id': str(c_id),
                'jinete_id': str(j_id),
                'preparador_id': str(p_id),
                'hipodromo_id': row.get('hipodromo', 'UNKNOWN'),
                'distancia': row.get('distancia', 1000),
                'pista': row.get('pista', 'ARENA'),
                'peso_fs': row.get('peso', 470),
                'mandil': row.get('numero', 0),
                'posicion': 0,  # Future
                'is_win': 0,
                'tiempo': 0,
                'padre': '0'
            }
            
            mapped_rows.append(input_row)
        
        df_future = pd.DataFrame(mapped_rows)
        
        # Prepare for FE transform
        cols_needed = ['fecha', 'caballo_id', 'jinete_id', 'preparador_id', 
                       'hipodromo_id', 'distancia', 'pista', 'peso_fs', 
                       'mandil', 'posicion', 'is_win', 'padre', 'tiempo']
        
        # Ensure history compatibility
        if 'preparador_id' not in self.history.columns:
            if 'stud_id' in self.history.columns:
                self.history['preparador_id'] = self.history['stud_id']
            else:
                self.history['preparador_id'] = '0'
        
        if 'padre' not in self.history.columns:
            self.history['padre'] = '0'
        
        if 'peso' in self.history.columns and 'peso_fs' not in self.history.columns:
            self.history['peso_fs'] = self.history['peso']
        
        common_cols = list(set(self.history.columns) & set(cols_needed))
        
        # Filter history to relevant horses (memory optimization)
        relevant_horses = df_future['caballo_id'].unique()
        hist_subset = self.history[self.history['caballo_id'].isin(relevant_horses)][common_cols].copy()
        
        df_future_input = df_future[common_cols]
        
        logger.info(f"   Concatenating history ({len(hist_subset):,}) + future ({len(df_future_input):,})...")
        df_combined = pd.concat([hist_subset, df_future_input], ignore_index=True)
        
        # Transform with FE
        logger.info(f"   Applying feature engineering...")
        df_transformed = self.fe.transform(df_combined, is_training=False)
        
        # Extract future rows (last N rows after sorting by date in FE)
        future_indices = range(len(hist_subset), len(df_combined))
        X_future = df_transformed.iloc[future_indices].copy()
        
        logger.info(f"✅ Features ready: {X_future.shape[1]} columns, {len(X_future)} rows")
        
        return X_future, df_program
    
    def _predict_with_calibration(self, X_future, df_program_enriched):
        """
        Genera predicciones y aplica calibración de probabilidades
        
        Returns:
            list of prediction dicts
        """
        # --- INICIO CORRECCIÓN ---
        # 1. Sanitizar columna 'numero' y 'nro_carrera': Rellenar NaN con 0 y forzar int
        # Esto previene ValueError: cannot convert float NaN to integer
        if 'numero' in df_program_enriched.columns:
            df_program_enriched['numero'] = df_program_enriched['numero'].fillna(0).astype(int)
            
        if 'nro_carrera' in df_program_enriched.columns:
            df_program_enriched['nro_carrera'] = df_program_enriched['nro_carrera'].fillna(0).astype(int)
        # --------------------------

        # Predict with ensemble
        logger.info("   Ejecutando ensemble (LightGBM + XGBoost + CatBoost)...")
        raw_scores = self.ensemble.predict(X_future)
        
        # Attach scores to program
        df_program = df_program_enriched.copy()
        df_program['raw_score'] = raw_scores
        
        # Apply softmax per race
        logger.info("   Aplicando calibración de probabilidades...")
        
        results = []
        
        for race_id, group in df_program.groupby('race_unique_id'):
            scores = group['raw_score'].values
            
            # 🎯 PROFESSIONAL CALIBRATION
            score_min = scores.min()
            score_max = scores.max()
            score_range = score_max - score_min
            
            if score_range > 1e-6:
                # 1. Normalize to [0, 1]
                normalized = (scores - score_min) / score_range
                
                # 2. Amplify differences
                amplified = normalized ** self.amplification_power
                
                # 3. Temperature scaling
                scaled = amplified / self.temperature
                
                # 4. Softmax with numerical stability
                exp_scores = np.exp(scaled - np.max(scaled))
                probs = exp_scores / np.sum(exp_scores)
            else:
                # All scores identical → uniform
                probs = np.ones(len(scores)) / len(scores)
                logger.warning(f"Race {race_id}: Scores uniformes ({score_min:.3f})")
            
            # Map back
            group = group.copy()
            group['prob_win'] = probs
            
            # Format results
            for idx, r in group.iterrows():
                # Safe conversion for possibly NaN values
                try:
                    carrera_num = int(r['nro_carrera']) if pd.notnull(r['nro_carrera']) else 0
                    mandil_num = int(r['numero']) if pd.notnull(r['numero']) else 0
                except (ValueError, TypeError):
                    carrera_num = 0
                    mandil_num = 0
                
                results.append({
                    'fecha': str(r['fecha']).split()[0],  # YYYY-MM-DD
                    'hipodromo': r['hipodromo'],
                    'carrera': carrera_num,
                    'numero': mandil_num,
                    'caballo': r['caballo'],
                    'probabilidad': round(r['prob_win'] * 100, 1)
                })
        
        logger.info(f"✅ Predicciones calibradas para {len(results)} caballos")
        
        return results
    
    def save_results(self, results):
        """Guarda resultados en JSON y SQLite"""
        # Save to JSON
        path = 'data/predicciones_activas.json'
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(results, f, default=str, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Guardado JSON: {path} ({len(results)} predicciones)")
        
        # Save to SQLite (optional, for backwards compatibility)
        try:
            import sqlite3
            df = pd.DataFrame(results)
            conn = sqlite3.connect('data/db/hipica_data.db')
            df.to_sql('predicciones_activas', conn, if_exists='replace', index=False)
            conn.close()
            logger.info(f"✅ Guardado SQLite: predicciones_activas table")
        except Exception as e:
            logger.warning(f"⚠️ No se pudo guardar en SQLite: {e}")


if __name__ == "__main__":
    try:
        pipeline = EnsembleInferencePipeline()
        pipeline.run()
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}")
        sys.exit(1)
