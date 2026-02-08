import pandas as pd
import numpy as np
import joblib
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeatureStore:
    """
    Lightweight Feature Store for efficient inference.
    Stores the current state of horses, jockeys, and trainers to avoid 
    recalculating full history on every prediction.
    """
    
    def __init__(self):
        # --- State Dictionaries ---
        
        # Horse State: 
        # { 'caballo_id': {
        #     'total_races': int,
        #     'total_wins': int,
        #     'last_date': datetime,
        #     'last_3_speeds': list,
        #     'last_3_positions': list
        #   } 
        # }
        self.horse_stats = {}
        
        # Track State per Horse:
        # { 'caballo_id': { 'hipodromo_id': { 'wins': int, 'runs': int } } }
        self.horse_track_stats = {}
        
        # Distance State per Horse:
        # { 'caballo_id': { 'dist_cat': { 'wins': int, 'runs': int } } }
        self.horse_dist_stats = {}
        
        # Duo State (Jockey + Trainer):
        # { (jinete_id, preparador_id): { 'wins': int, 'runs': int } }
        self.duo_stats = {}
        
        # Sire State (Cold Start):
        # { 'padre_name': { 'wins': int, 'runs': int } }
        self.sire_stats = {}
        
        self.last_updated = None

    def _get_dist_cat(self, distancia):
        """Helper to categorize distance"""
        try:
            d = float(distancia)
            if d < 1100: return 'sprint'
            if d <= 1400: return 'mile'
            return 'long'
        except:
            return 'sprint'

    def _clean_time(self, t):
        """Helper to parse time string to seconds"""
        try:
            parts = str(t).split('.')
            if len(parts) >= 2:
                seconds = float(parts[0])*60 + float(parts[1])
                if len(parts) > 2:
                    seconds += float(parts[2])/100
                return seconds
            return 0
        except:
            return 0

    def update(self, df_history):
        """
        Updates the store with new historical records.
        Assumes df_history is sorted by date.
        """
        if df_history.empty:
            return

        # Ensure datetime
        if not pd.api.types.is_datetime64_any_dtype(df_history['fecha']):
            df_history = df_history.copy()
            df_history['fecha'] = pd.to_datetime(df_history['fecha'])
            
        logger.info(f"Updating Feature Store with {len(df_history)} records...")
        
        for idx, row in df_history.iterrows():
            self._update_single_row(row)
            
        self.last_updated = datetime.now()
        logger.info("Feature Store updated successfully.")

    def _update_single_row(self, row):
        """Updates state based on a SINGLE race result row."""
        
        # Extract keys
        c_id = str(row['caballo_id'])
        j_id = str(row['jinete_id'])
        p_id = str(row.get('preparador_id', '0'))
        h_id = str(row['hipodromo_id'])
        padre = str(row.get('padre', '0'))
        
        # Outcome
        pos = r_pos = 0
        try:
            pos = int(float(row['posicion'])) if pd.notna(row['posicion']) else 0
        except:
            pos = 0
            
        is_win = 1 if pos == 1 else 0
        
        # --- Update Horse Global Stats ---
        if c_id not in self.horse_stats:
            self.horse_stats[c_id] = {
                'total_races': 0, 'total_wins': 0, 
                'last_date': None, 
                'last_3_speeds': [], 'last_3_positions': []
            }
            
        stats = self.horse_stats[c_id]
        stats['total_races'] += 1
        stats['total_wins'] += is_win
        stats['last_date'] = row['fecha']
        
        # Speed
        dist = float(row['distancia']) if pd.notna(row['distancia']) else 1000
        seconds = self._clean_time(row.get('tiempo', 0))
        speed_mps = (dist / seconds) if seconds > 0 else 0
        
        if speed_mps > 0:
            stats['last_3_speeds'].append(speed_mps)
            if len(stats['last_3_speeds']) > 3:
                stats['last_3_speeds'].pop(0)
                
        # Position (Trend)
        if pos > 0:
            stats['last_3_positions'].append(pos)
            if len(stats['last_3_positions']) > 3:
                stats['last_3_positions'].pop(0)

        # --- Update Track Stats ---
        if c_id not in self.horse_track_stats:
            self.horse_track_stats[c_id] = {}
        if h_id not in self.horse_track_stats[c_id]:
            self.horse_track_stats[c_id][h_id] = {'wins': 0, 'runs': 0}
            
        self.horse_track_stats[c_id][h_id]['runs'] += 1
        self.horse_track_stats[c_id][h_id]['wins'] += is_win

        # --- Update Distance Stats ---
        dist_cat = self._get_dist_cat(dist)
        if c_id not in self.horse_dist_stats:
            self.horse_dist_stats[c_id] = {}
        if dist_cat not in self.horse_dist_stats[c_id]:
            self.horse_dist_stats[c_id][dist_cat] = {'wins': 0, 'runs': 0}
            
        self.horse_dist_stats[c_id][dist_cat]['runs'] += 1
        self.horse_dist_stats[c_id][dist_cat]['wins'] += is_win

        # --- Update Duo Stats ---
        duo_key = (j_id, p_id)
        if duo_key not in self.duo_stats:
            self.duo_stats[duo_key] = {'wins': 0, 'runs': 0}
        
        self.duo_stats[duo_key]['runs'] += 1
        self.duo_stats[duo_key]['wins'] += is_win
        
        # --- Update Sire Stats ---
        if padre not in self.sire_stats:
            self.sire_stats[padre] = {'wins': 0, 'runs': 0}
            
        self.sire_stats[padre]['runs'] += 1
        self.sire_stats[padre]['wins'] += is_win

    def get_features(self, candidate_row):
        """
        Returns a feature dictionary for a single candidate row (inference).
        candidate_row should have: caballo_id, jinete_id, preparador_id, hipodromo_id, fecha, distancia, padre
        """
        c_id = str(candidate_row['caballo_id'])
        j_id = str(candidate_row['jinete_id'])
        p_id = str(candidate_row.get('preparador_id', '0'))
        h_id = str(candidate_row['hipodromo_id'])
        padre = str(candidate_row.get('padre', '0'))
        race_date = pd.to_datetime(candidate_row['fecha'])
        d_val = candidate_row.get('distancia')
        dist = float(d_val) if d_val is not None else 1000.0

        feats = {}
        
        # Defaults
        h_stats = self.horse_stats.get(c_id, {
            'total_races': 0, 'total_wins': 0, 
            'last_date': None, 'last_3_speeds': [], 'last_3_positions': []
        })
        
        # 1. Global Win Rate
        runs = h_stats['total_races']
        wins = h_stats['total_wins']
        feats['win_rate'] = (wins / runs) if runs > 0 else 0.0
        feats['races_count'] = runs
        
        # 2. Track Win Rate
        t_stats = self.horse_track_stats.get(c_id, {}).get(h_id, {'runs': 0, 'wins': 0})
        feats['track_win_rate'] = (t_stats['wins'] / t_stats['runs']) if t_stats['runs'] > 0 else 0.0

        # 3. Distance Win Rate
        dist_cat = self._get_dist_cat(dist)
        d_stats = self.horse_dist_stats.get(c_id, {}).get(dist_cat, {'runs': 0, 'wins': 0})
        feats['dist_win_rate'] = (d_stats['wins'] / d_stats['runs']) if d_stats['runs'] > 0 else 0.0
        
        # 4. Duo Efficiency
        duo = self.duo_stats.get((j_id, p_id), {'runs': 0, 'wins': 0})
        feats['duo_eff'] = (duo['wins'] / duo['runs']) if duo['runs'] > 0 else 0.0
        
        # 5. Sire Win Rate (Cold Start)
        sire_s = self.sire_stats.get(padre, {'runs': 0, 'wins': 0})
        sire_wr = (sire_s['wins'] / sire_s['runs']) if sire_s['runs'] > 0 else 0.10
        feats['sire_win_rate'] = sire_wr
        
        # Reset win rate for debutants
        if runs == 0:
            feats['win_rate'] = sire_wr

        # 6. Days Rest
        if h_stats['last_date']:
            delta = (race_date - h_stats['last_date']).days
            feats['days_rest'] = max(0, delta)
        else:
            feats['days_rest'] = 30  # Default rest
            
        # 7. Momentum (Trend)
        # Slope of last 3 positions [p_t-3, p_t-2, p_t-1]
        last_pos = h_stats['last_3_positions']
        if len(last_pos) >= 2:
            # Simple trend: (Last - First)
            # If [10, 5, 2] -> 2 - 10 = -8 (Improvement)
            feats['trend_3'] = last_pos[-1] - last_pos[0]
        else:
            feats['trend_3'] = 0.0
            
        # 8. Avg Speed (Last 3)
        speeds = h_stats['last_3_speeds']
        if speeds:
            feats['avg_speed_3'] = sum(speeds) / len(speeds)
        else:
            feats['avg_speed_3'] = 14.0 # Default speed m/s
            
        # Static Pass-through (needed for model)
        # Imputer will handle NaNs if any, but we should provide RAW values expected by model
        
        p_val = candidate_row.get('peso_fs')
        feats['peso'] = float(p_val) if p_val is not None else 470.0
        
        m_val = candidate_row.get('mandil')
        feats['mandil'] = float(m_val) if m_val is not None else 0.0
        
        feats['distancia'] = dist
        
        return feats

    def save(self, path='data/feature_store.pkl'):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self, path)
        logger.info(f"Feature Store saved to {path}")

    @staticmethod
    def load(path='data/feature_store.pkl'):
        if not os.path.exists(path):
            logger.warning(f"Feature Store not found at {path}. Returning empty store.")
            return FeatureStore()
        return joblib.load(path)
