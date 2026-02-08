"""
Pipeline de Inferencia Optimizado v5.0
--------------------------------------
Usa LightGBM optimizado con features de alta señal para predicciones.

Author: ML Engineering Team
Date: 2026-02-07
"""

import pandas as pd
import numpy as np
import os
import json
import sys
import logging
import joblib
from datetime import datetime
from src.models.data_manager import cargar_programa

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if sys.platform == "win32" and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


class OptimizedInferencePipeline:
    """
    Pipeline de inferencia usando LightGBM optimizado v5.0
    """
    
    def __init__(self,
                 model_path='src/models/lgbm_optimized_latest.pkl',
                 fe_path='src/models/feature_eng_v5_latest.pkl',
                 calibrator_path='src/models/calibrator_v5.pkl'):
        self.model_path = model_path
        self.fe_path = fe_path
        self.calibrator_path = calibrator_path
        self.model = None
        self.fe = None
        self.calibrator = None
        
        # Cache de estadísticas históricas
        self.horse_stats = {}
        self.jockey_stats = {}
        self.track_stats = {}
        self.trainer_stats = {}  # NUEVO: stats de preparadores
    
    def load_artifacts(self):
        """Carga modelo, feature engineering y calibrador."""
        logger.info("Cargando artefactos...")
        
        # Modelo
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Modelo no encontrado: {self.model_path}")
        self.model = joblib.load(self.model_path)
        logger.info(f"✅ Modelo cargado: {self.model_path}")
        
        # Feature Engineering
        if os.path.exists(self.fe_path):
            try:
                self.fe = joblib.load(self.fe_path)
                logger.info(f"✅ Feature Eng cargado: {self.fe_path}")
            except Exception as e:
                logger.warning(f"⚠️ FE pickle error, usando inline: {e}")
                self.fe = None
        else:
            logger.warning(f"⚠️ FE no encontrado, usando defaults")
            
        # Calibrador
        if os.path.exists(self.calibrator_path):
            self.calibrator = joblib.load(self.calibrator_path)
            logger.info(f"✅ Calibrador cargado: {self.calibrator_path}")
        else:
            logger.warning(f"⚠️ Calibrador no encontrado, usando heurístico")
    
    def _load_historical_stats(self):
        """Carga estadísticas históricas para features."""
        import sqlite3
        
        try:
            conn = sqlite3.connect('data/db/hipica_data.db')
            
            # Estadísticas de caballos
            horse_query = """
            SELECT 
                c.id as caballo_id,
                c.nombre as caballo,
                COUNT(*) as races,
                SUM(CASE WHEN p.posicion = 1 THEN 1 ELSE 0 END) as wins,
                AVG(CASE WHEN p.posicion <= 3 THEN 1 ELSE 0 END) as top3_rate
            FROM participaciones p
            JOIN caballos c ON p.caballo_id = c.id
            GROUP BY c.id
            """
            horses = pd.read_sql(horse_query, conn)
            self.horse_stats = {
                row['caballo_id']: {
                    'races': row['races'],
                    'wins': row['wins'],
                    'win_rate': row['wins'] / row['races'] if row['races'] > 0 else 0,
                    'top3_rate': row['top3_rate'] or 0
                }
                for _, row in horses.iterrows()
            }
            
            # Estadísticas de jinetes
            jockey_query = """
            SELECT 
                j.id as jinete_id,
                j.nombre as jinete,
                COUNT(*) as races,
                SUM(CASE WHEN p.posicion = 1 THEN 1 ELSE 0 END) as wins
            FROM participaciones p
            JOIN jinetes j ON p.jinete_id = j.id
            GROUP BY j.id
            """
            jockeys = pd.read_sql(jockey_query, conn)
            self.jockey_stats = {
                row['jinete_id']: {
                    'races': row['races'],
                    'wins': row['wins'],
                    'win_rate': row['wins'] / row['races'] if row['races'] > 0 else 0.08
                }
                for _, row in jockeys.iterrows()
            }
            
            # Estadísticas jinete-pista
            jt_query = """
            SELECT 
                j.id as jinete_id,
                h.id as hipodromo_id,
                COUNT(*) as races,
                SUM(CASE WHEN p.posicion = 1 THEN 1 ELSE 0 END) as wins
            FROM participaciones p
            JOIN jinetes j ON p.jinete_id = j.id
            JOIN carreras car ON p.carrera_id = car.id
            JOIN jornadas jor ON car.jornada_id = jor.id
            JOIN hipodromos h ON jor.hipodromo_id = h.id
            GROUP BY j.id, h.id
            """
            jt = pd.read_sql(jt_query, conn)
            self.track_stats = {}
            for _, row in jt.iterrows():
                key = (row['jinete_id'], row['hipodromo_id'])
                self.track_stats[key] = {
                    'races': row['races'],
                    'win_rate': row['wins'] / row['races'] if row['races'] > 0 else 0.08
                }
            
            # Estadísticas de preparadores (NUEVO)
            try:
                trainer_query = """
                SELECT 
                    pc.stud_id as preparador_id,
                    COUNT(*) as races,
                    SUM(CASE WHEN p.posicion = 1 THEN 1 ELSE 0 END) as wins
                FROM participaciones p
                JOIN programa_carreras pc ON p.caballo_id = pc.caballo_id
                GROUP BY pc.stud_id
                HAVING races > 0
                """
                trainers = pd.read_sql(trainer_query, conn)
                self.trainer_stats = {
                    row['preparador_id']: {
                        'races': row['races'],
                        'win_rate': row['wins'] / row['races'] if row['races'] > 0 else 0.08
                    }
                    for _, row in trainers.iterrows() if row['preparador_id']
                }
            except:
                self.trainer_stats = {}
            
            conn.close()
            logger.info(f"✅ Stats cargadas: {len(self.horse_stats)} caballos, {len(self.jockey_stats)} jinetes, {len(self.trainer_stats)} preparadores")
            
        except Exception as e:
            logger.warning(f"⚠️ Error cargando stats: {e}")
    
    def run(self):
        """Ejecuta el pipeline completo."""
        logger.info("=" * 70)
        logger.info("LIGHTGBM OPTIMIZADO v5.0 - INFERENCE PIPELINE")
        logger.info("=" * 70)
        
        try:
            # 1. Cargar artefactos
            self.load_artifacts()
            self._load_historical_stats()
            
            # 2. Cargar programa futuro
            logger.info("\n[PASO 1/4] Cargando programa de carreras...")
            df_program = cargar_programa(solo_futuras=True)
            
            if df_program.empty:
                logger.warning("⚠️ No hay carreras futuras")
                return
            
            logger.info(f"✅ Cargadas {len(df_program)} entradas")
            
            # 3. Preparar features
            logger.info("\n[PASO 2/4] Generando features...")
            X_future, df_enriched = self._prepare_features(df_program)
            
            logger.info(f"✅ Features: {X_future.shape[1]} columnas, {len(X_future)} filas")
            
            # 4. Predecir
            logger.info("\n[PASO 3/4] Generando predicciones...")
            predictions = self._predict(X_future, df_enriched)
            
            # 5. Guardar
            logger.info("\n[PASO 4/4] Guardando resultados...")
            self._save_results(predictions)
            
            logger.info("\n" + "=" * 70)
            logger.info(f"✅ INFERENCIA COMPLETADA: {len(predictions)} predicciones")
            logger.info("=" * 70)
            
        except Exception as e:
            logger.error(f"❌ Error: {e}", exc_info=True)
            raise
    
    def _prepare_features(self, df_program):
        """Prepara features para inferencia."""
        import sqlite3
        
        # Mapeo de IDs
        try:
            conn = sqlite3.connect('data/db/hipica_data.db')
            caballos = pd.read_sql("SELECT id, nombre FROM caballos", conn)
            jinetes = pd.read_sql("SELECT id, nombre FROM jinetes", conn)
            conn.close()
            
            c_map = dict(zip(caballos['nombre'], caballos['id']))
            j_map = dict(zip(jinetes['nombre'], jinetes['id']))
        except:
            c_map = {}
            j_map = {}
        
        hip_map = {
            'Club Hípico de Santiago': 1,
            'Hipódromo Chile': 2,
            'Valparaíso Sporting': 3,
            'Club Hípico de Concepción': 4
        }
        
        # Feature columns (DEBE COINCIDIR con entrenamiento)
        feature_cols = [
            'win_rate', 'races_count', 'recent_form', 'avg_speed_3',
            'track_win_rate', 'dist_win_rate',
            'jockey_win_rate', 'jockey_track_rate', 'trainer_win_rate', 'duo_eff',
            'trend_3', 'days_rest',
            'sire_win_rate',
            'peso', 'mandil', 'distancia'
        ]
        
        features_list = []
        enriched_rows = []
        
        for _, row in df_program.iterrows():
            # IDs
            c_name = row.get('caballo', 'Unknown')
            c_id = c_map.get(c_name, 0)
            j_name = row.get('jinete', '')
            j_id = j_map.get(j_name, 0)
            h_name = row.get('hipodromo', '')
            h_id = hip_map.get(h_name, 0)
            
            # Stats del caballo
            h_stats = self.horse_stats.get(c_id, {'races': 0, 'wins': 0, 'win_rate': 0})
            j_stats = self.jockey_stats.get(j_id, {'win_rate': 0.08})
            jt_key = (j_id, h_id)
            jt_stats = self.track_stats.get(jt_key, {'win_rate': 0.08})
            
            # Conversión segura de tipos numéricos (manejar None y formatos texto)
            def safe_float(val, default=0.0):
                if val is None or val == '' or val == 'None':
                    return default
                if isinstance(val, (int, float)):
                    if np.isnan(val) if isinstance(val, float) else False:
                        return default
                    return float(val)
                try:
                    # Limpiar texto: remover "m", "Mts.", etc
                    val_str = str(val).strip()
                    # Remover unidades comunes
                    val_str = val_str.replace('Mts.', '').replace('mts', '').replace('m', '')
                    val_str = val_str.replace('M', '').strip()
                    # Manejar formato "1.200" (miles con punto)
                    if '.' in val_str and len(val_str.split('.')[0]) <= 2:
                        # Es formato "1.200" => 1200
                        val_str = val_str.replace('.', '')
                    return float(val_str) if val_str else default
                except (ValueError, TypeError):
                    return default
            
            dist = safe_float(row.get('distancia'), 1200)
            
            # Construir features
            feats = {
                'win_rate': h_stats.get('win_rate', 0) if h_stats['races'] > 0 else 0.10,
                'races_count': h_stats.get('races', 0),
                'recent_form': 5.0,  # Default neutral
                'avg_speed_3': 14.0,  # Default
                'track_win_rate': 0.0,  # Necesitaría más datos
                'dist_win_rate': 0.0,
                'jockey_win_rate': j_stats.get('win_rate', 0.08),
                'jockey_track_rate': jt_stats.get('win_rate', 0.08),
                'trainer_win_rate': 0.08,  # Default, se actualizará abajo
                'duo_eff': 0.08,
                'trend_3': 0.0,
                'days_rest': 30,
                'sire_win_rate': 0.10,
                'peso': safe_float(row.get('peso'), 470),
                'mandil': safe_float(row.get('numero'), 0),
                'distancia': dist
            }
            
            features_list.append(feats)
            
            # Enriquecer fila
            row_copy = row.copy()
            row_copy['caballo_id'] = c_id
            row_copy['jinete_id'] = j_id
            row_copy['hipodromo_id'] = h_id
            enriched_rows.append(row_copy)
        
        X = pd.DataFrame(features_list)[feature_cols]
        X = X.fillna(0)
        
        df_enriched = pd.DataFrame(enriched_rows)
        
        # Race ID para agrupación
        df_enriched['race_unique_id'] = (
            df_enriched['fecha'].astype(str) + "_" +
            df_enriched['hipodromo'].astype(str) + "_" +
            df_enriched['nro_carrera'].astype(str)
        )
        
        return X, df_enriched
    
    def _predict(self, X, df_enriched):
        """Genera predicciones calibradas."""
        # Raw scores
        raw_scores = self.model.predict(X)
        
        # Calibración
        if self.calibrator:
            probs = self.calibrator.transform(raw_scores)
            probs = np.clip(probs, 0.01, 0.99)
        else:
            # Heurístico si no hay calibrador
            s_min, s_max = raw_scores.min(), raw_scores.max()
            if s_max > s_min:
                probs = (raw_scores - s_min) / (s_max - s_min)
                probs = probs ** 1.2  # Ajuste
            else:
                probs = np.ones(len(raw_scores)) * 0.1
        
        df_enriched['prob_raw'] = probs
        
        # Normalización por carrera
        results = []
        
        for race_id, group in df_enriched.groupby('race_unique_id'):
            probs_race = group['prob_raw'].values
            
            # Softmax suave
            exp_probs = np.exp(probs_race * 3)  # Temperatura
            probs_normalized = exp_probs / exp_probs.sum()
            
            for i, (idx, row) in enumerate(group.iterrows()):
                try:
                    carrera_num = int(row['nro_carrera']) if pd.notnull(row['nro_carrera']) else 0
                    mandil_num = int(row['numero']) if pd.notnull(row['numero']) else 0
                except:
                    carrera_num = 0
                    mandil_num = 0
                
                results.append({
                    'fecha': str(row['fecha']).split()[0],
                    'hipodromo': row['hipodromo'],
                    'carrera': carrera_num,
                    'numero': mandil_num,
                    'caballo': row['caballo'],
                    'jinete': row.get('jinete', ''),
                    'probabilidad': round(probs_normalized[i] * 100, 1)
                })
        
        logger.info(f"✅ {len(results)} predicciones generadas")
        return results
    
    def _save_results(self, results):
        """Guarda resultados."""
        # JSON
        json_path = 'data/predicciones_activas.json'
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, default=str, indent=2, ensure_ascii=False)
        logger.info(f"✅ JSON: {json_path}")
        
        # SQLite
        try:
            import sqlite3
            df = pd.DataFrame(results)
            conn = sqlite3.connect('data/db/hipica_data.db')
            df.to_sql('predicciones_activas', conn, if_exists='replace', index=False)
            conn.close()
            logger.info(f"✅ SQLite: predicciones_activas")
        except Exception as e:
            logger.warning(f"⚠️ SQLite error: {e}")


if __name__ == "__main__":
    try:
        pipeline = OptimizedInferencePipeline()
        pipeline.run()
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        sys.exit(1)
