"""
Pipeline de Inferencia para Ensemble v4
Usa EnsembleRanker (LightGBM + XGBoost + CatBoost) para predicciones

Author: ML Engineering Team
Date: 2025-12-28
Version: 4.2 (Isotonic Calibration)
"""

import pandas as pd
import numpy as np
import os
import json
import sys
import logging
import time
import gc
import joblib
from datetime import datetime
from src.models.data_manager import cargar_programa
from src.models.ensemble_ranker import EnsembleRanker
from src.models.feature_store import FeatureStore

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
    """Pipeline de inferencia usando Ensemble v4 y Feature Store + Calibrador"""
    
    def __init__(self, 
                 ensemble_path='src/models/ensemble_latest.pkl',
                 feature_store_path='data/feature_store.pkl',
                 calibrator_path='src/models/calibrator_v4.pkl'):
        """
        Args:
            ensemble_path: Ruta al ensemble guardado
            feature_store_path: Ruta al Feature Store
            calibrator_path: Ruta al calibrador Isotonic
        """
        self.ensemble_path = ensemble_path
        self.feature_store_path = feature_store_path
        self.calibrator_path = calibrator_path
        self.ensemble = None
        self.store = None
        self.calibrator = None
        
    def load_artifacts(self):
        """Carga modelos, Feature Store y Calibrador"""
        # Verificar existencia de ensemble
        if not os.path.exists(self.ensemble_path):
            raise FileNotFoundError(f"Ensemble not found: {self.ensemble_path}")
        
        # Enforce Feature Store
        if not os.path.exists(self.feature_store_path):
             logger.warning(f"Feature Store not found at {self.feature_store_path}. Creating empty store (Cold Start).")
        
        start = time.time()
        
        # Cargar ensemble
        self.ensemble = EnsembleRanker.load(self.ensemble_path)
        
        # Cargar Feature Store
        self.store = FeatureStore.load(self.feature_store_path)
        
        # Cargar Calibrador
        if os.path.exists(self.calibrator_path):
            self.calibrator = joblib.load(self.calibrator_path)
            logger.info(f"✅ Calibrador Isotonic cargado: {self.calibrator_path}")
        else:
            logger.warning(f"⚠️ Calibrator not found at {self.calibrator_path}. Probs will be uncalibrated.")
            self.calibrator = None
        
        logger.info("Artifacts loaded", extra={
            'ensemble_path': self.ensemble_path,
            'feature_store_path': self.feature_store_path,
            'calibrator_path': self.calibrator_path,
            'load_time_ms': int((time.time() - start) * 1000)
        })
        
    def run(self):
        """Ejecuta el pipeline completo de inferencia"""
        start_time = time.time()
        logger.info("="*70)
        logger.info("ENSEMBLE V4 INFERENCE PIPELINE (Calibrated)")
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
            
            # 3. Transform features
            logger.info("\n[PASO 2/4] Consultando Feature Store (O(1))...")
            X_future, df_program_enriched = self._prepare_features(df_program)
            
            # 4. Predict
            logger.info("\n[PASO 3/4] Generando predicciones calibradas...")
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
        Prepara features para inferencia usando Feature Store.
        Using same logic as v4.1 but consolidated.
        """
        # Create race IDs for grouping
        df_program['race_unique_id'] = (
            df_program['fecha'].astype(str) + "_" + 
            df_program['hipodromo'] + "_" + 
            df_program['nro_carrera'].astype(str)
        )
        
        # Explicit feature columns (MUST match training)
        feature_cols = [
            'days_rest', 'win_rate', 'races_count', 'avg_speed_3',
            'track_win_rate', 'dist_win_rate', 
            'duo_eff',
            'trend_3',
            'sire_win_rate',
            'peso', 'mandil', 'distancia'
        ]
        
        # ID Mappers
        import sqlite3
        try:
            conn = sqlite3.connect('data/db/hipica_data.db')
            caballos = pd.read_sql("SELECT id, nombre FROM caballos", conn)
            jinetes = pd.read_sql("SELECT id, nombre FROM jinetes", conn)
            studs = pd.read_sql("SELECT id, nombre FROM studs", conn)
            conn.close()
            
            c_map = dict(zip(caballos['nombre'], caballos['id']))
            j_map = dict(zip(jinetes['nombre'], jinetes['id']))
            s_map = dict(zip(studs['nombre'], studs['id']))
        except Exception as e:
            logger.warning(f"Feature Store Map Load Error: {e}")
            c_map = {}; j_map = {}; s_map = {}
            
        hip_map = {
            'Club Hípico de Santiago': '1',
            'Hipódromo Chile': '2',
            'Valparaíso Sporting': '3',
            'Club Hípico de Concepción': '4'
        }
        
        features_list = []
        enriched_rows = []
        
        for idx, row in df_program.iterrows():
            c_name = row.get('caballo', 'Unknown')
            # ID resolution
            c_id = str(c_map.get(c_name, 0))
            j_id = str(j_map.get(row.get('jinete', ''), 0))
            p_id = str(s_map.get(row.get('stud', ''), 0))
            h_name = row.get('hipodromo', 'UNKNOWN')
            h_id = hip_map.get(h_name, '0')

            candidate = {
                'caballo_id': c_id,
                'jinete_id': j_id,
                'preparador_id': p_id,
                'hipodromo_id': h_id,
                'fecha': row['fecha'],
                'distancia': row.get('distancia', 1000),
                'padre': '0', 
                'mandil': row.get('numero', 0),
                'peso_fs': row.get('peso', 470)
            }
            
            # Lookup
            feats = self.store.get_features(candidate)
            features_list.append(feats)
            
            row_enriched = row.copy()
            row_enriched['caballo_id'] = c_id
            enriched_rows.append(row_enriched)
            
        # Create X DataFrame
        X_future = pd.DataFrame(features_list)
        
        # Ensure correct columns and order
        for col in feature_cols:
            if col not in X_future.columns:
                X_future[col] = 0.0
                
        X_future = X_future[feature_cols].fillna(0)
        
        return X_future, pd.DataFrame(enriched_rows)
    
    def _predict_with_calibration(self, X_future, df_program_enriched):
        """
        Genera predicciones y aplica calibración de probabilidades
        """
        # Sanitizar data types
        if 'numero' in df_program_enriched.columns:
            df_program_enriched['numero'] = df_program_enriched['numero'].fillna(0).astype(int)
        if 'nro_carrera' in df_program_enriched.columns:
            df_program_enriched['nro_carrera'] = df_program_enriched['nro_carrera'].fillna(0).astype(int)

        # 1. Raw Scores
        logger.info("   Obteniendo raw scores del Ensemble...")
        raw_scores = self.ensemble.predict(X_future)
        
        # 2. Calibration
        df_program = df_program_enriched.copy()
        
        if self.calibrator:
            logger.info("   Aplicando Isotonic Calibration...")
            # Ensure shape
            calibrated_probs = self.calibrator.transform(raw_scores)
            
            # Clip strict [0, 1] just in case
            calibrated_probs = np.clip(calibrated_probs, 0.0, 1.0)
            
            df_program['prob_win'] = calibrated_probs
        else:
            # Fallback (Manual Softmaxish)
            logger.warning("   Using fallback heuristic calibration.")
            s_min, s_max = raw_scores.min(), raw_scores.max()
            if s_max > s_min:
                norm = (raw_scores - s_min) / (s_max - s_min)
                df_program['prob_win'] = norm ** 1.6
            else:
                df_program['prob_win'] = 0.1

        # 3. Race-level Normalization
        results = []
        
        for race_id, group in df_program.groupby('race_unique_id'):
            probs = group['prob_win'].values
            
            # Normalizar para que sume 100% (Probabilidad de ganar ESTA carrera)
            total_prob = probs.sum()
            
            if total_prob > 0:
                probs_normalized = probs / total_prob
            else:
                probs_normalized = np.ones(len(probs)) / len(probs)
            
            group = group.copy()
            group['prob_final'] = probs_normalized
            
            # Format results
            for idx, r in group.iterrows():
                try:
                    carrera_num = int(r['nro_carrera']) if pd.notnull(r['nro_carrera']) else 0
                    mandil_num = int(r['numero']) if pd.notnull(r['numero']) else 0
                except:
                    carrera_num = 0; mandil_num = 0
                
                results.append({
                    'fecha': str(r['fecha']).split()[0],
                    'hipodromo': r['hipodromo'],
                    'carrera': carrera_num,
                    'numero': mandil_num,
                    'caballo': r['caballo'],
                    'jinete': r.get('jinete', ''),
                    'probabilidad': round(r['prob_final'] * 100, 1)
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
        
        logger.info(f"✅ Guardado JSON: {path}")
        
        # Save to SQLite
        try:
            import sqlite3
            df = pd.DataFrame(results)
            conn = sqlite3.connect('data/db/hipica_data.db')
            df.to_sql('predicciones_activas', conn, if_exists='replace', index=False)
            conn.close()
            logger.info(f"✅ Guardado SQLite: predicciones_activas")
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
