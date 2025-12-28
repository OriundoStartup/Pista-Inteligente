import pandas as pd
import numpy as np
import joblib
import os
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder

class FeatureEngineering(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.imputer = None
        self.encoders = {}
        # New Feature Columns
        self.feature_cols = [
            # Basic
            'days_rest', 'win_rate', 'races_count', 'avg_speed_3',
            # Context
            'track_win_rate', 'dist_win_rate', 
            # Duo
            'duo_eff',
            # Momentum
            'trend_3',
            # Cold Start (Sire)
            'sire_win_rate',
            # Static
            'peso', 'mandil', 'distancia'
        ]

    def _clean_time(self, t):
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

    def fit(self, df, y=None):
        """Fit encoders and imputer on training data."""
        # We don't really 'learn' the historical aggregates here because they are dynamic rolling features.
        # But we DO need to fit the Imputer on the TRANSFORMED training set.
        # So we just setup encoders here.
        
        # Pista Encoder (for consistency, though we use numeric win rate now)
        # We might still want to keep raw track encoded if the tree can learn from it.
        # For this Phase 1 request, I focus on the requested features, but let's keep it robust.
        return self

    def transform(self, df, is_training=True):
        """Generate features efficiently using Pandas Vectorized Operations."""
        df = df.copy()
        
        # --- PREPROCESSING ---
        df['fecha'] = pd.to_datetime(df['fecha'])
        
        # ✅ CRÍTICO: Ordenar por caballo Y fecha para evitar leakage
        df = df.sort_values(['caballo_id', 'fecha']).reset_index(drop=True)
        
        # Validación anti-leakage
        grouped_check = df.groupby('caballo_id')['fecha']
        if not grouped_check.apply(lambda x: x.is_monotonic_increasing).all():
            raise ValueError("❌ LEAKAGE RISK: Fechas no están ordenadas correctamente por caballo")
        
        # Numeric conversions
        df['posicion'] = pd.to_numeric(df['posicion'], errors='coerce').fillna(0)
        df['is_win'] = (df['posicion'] == 1).astype(float)
        
        df['distancia'] = pd.to_numeric(df['distancia'], errors='coerce').fillna(1000)
        df['mandil'] = pd.to_numeric(df['mandil'], errors='coerce').fillna(0)
        df['peso'] = pd.to_numeric(df['peso_fs'], errors='coerce').fillna(470)
        
        # Clean ID columns for grouping
        for col in ['caballo_id', 'jinete_id', 'preparador_id', 'hipodromo_id', 'padre']:
            if col in df.columns:
                df[col] = df[col].fillna(0).astype(str)

        # --- FEATURE ENGINEERING ---
        
        # 1. Global History (Win Rate & Count)
        # Shift(1) ensures we don't use current race result
        grouped_horse = df.groupby('caballo_id')
        
        prev_wins = grouped_horse['is_win'].shift(1).expanding().sum()
        prev_count = grouped_horse['is_win'].shift(1).expanding().count().fillna(0)
        
        df['win_rate'] = (prev_wins / prev_count).fillna(0)
        df['races_count'] = prev_count

        # 2. Context: Track Win Rate
        # Group by [Caballo, Hipodromo]
        # BUT transforming back to original index is tricky with multiple keys.
        # Solution: Sort by date (already done), then GroupBy multiple keys, calculate expanding, shift.
        
        # We must ensure the index alignment.
        # GroupBy maintains the index of the original dataframe rows? Yes.
        
        # Calculate Track Hist
        grouped_track = df.groupby(['caballo_id', 'hipodromo_id'])
        track_wins = grouped_track['is_win'].shift(1).expanding().sum()
        track_cnt = grouped_track['is_win'].shift(1).expanding().count()
        df['track_win_rate'] = (track_wins / track_cnt).fillna(0) # Default 0 if no history at this track
        
        # 3. Context: Distance Category Win Rate
        # Bin distances: Sprint (<1100), Mid (1100-1400), Long (>1400)
        conditions = [
            (df['distancia'] < 1100),
            (df['distancia'] >= 1100) & (df['distancia'] <= 1400),
            (df['distancia'] > 1400)
        ]
        choices = ['sprint', 'mile', 'long']
        df['dist_cat'] = np.select(conditions, choices, default='sprint')
        
        grouped_dist = df.groupby(['caballo_id', 'dist_cat'])
        dist_wins = grouped_dist['is_win'].shift(1).expanding().sum()
        dist_cnt = grouped_dist['is_win'].shift(1).expanding().count()
        df['dist_win_rate'] = (dist_wins / dist_cnt).fillna(0)

        # 4. Duo: Jockey + Trainer (Dynamic Duo)
        # Using 'preparador_id' (which is stud_id in our hack)
        if 'preparador_id' in df.columns:
            grouped_duo = df.groupby(['jinete_id', 'preparador_id'])
            duo_wins = grouped_duo['is_win'].shift(1).expanding().sum()
            duo_cnt = grouped_duo['is_win'].shift(1).expanding().count()
            # Bayesian Average for stability: (wins + 1) / (races + 2) roughly, or just simple rate with default
            # Let's clean simple rate but default to global mean? 
            # Request asked for "Win Rate", imply simple.
            df['duo_eff'] = (duo_wins / duo_cnt).fillna(0) 
        else:
            df['duo_eff'] = 0.0

        # 5. Momentum: Last 3 Races Trend
        # We need the slope of positions. 
        # Only feasible if we have 3 races.
        # Slope of [pos_t-3, pos_t-2, pos_t-1]. 
        # If pos decreases (10 -> 5 -> 1), slope is negative (Good momentum).
        # We can implement simple linear regression slope or just (Pos_recent - Pos_old) / 2
        
        # Get last 3 positions
        # rolling(3) includes current? We need shift(1) first.
        
        # Create a helper for slope
        def calc_slope(x):
            if len(x) < 3: return 0
            # x is [p1, p2, p3] (oldest to newest)
            # x = [10, 5, 1]. indices=[0, 1, 2].
            # polyfit(indices, values, 1)[0] is slope
            try:
                ts = np.arange(len(x))
                if np.std(ts) == 0: return 0
                return np.polyfit(ts, x, 1)[0]
            except:
                return 0

        # Pandas rolling apply is slow. 
        # Faster proxy: (Last - Avg_Rest) or (Pos_t-1 - Pos_t-3)
        # Let's use (Last - First) of the window as simple trend proxy.
        # (Pos_t-1 - Pos_t-3).
        # If result is -5 (e.g. 2 - 7), it means improvement.
        
        prev_pos = df.groupby('caballo_id')['posicion'].shift(1) # Pos t-1
        prev_pos_3 = df.groupby('caballo_id')['posicion'].shift(3) # Pos t-3
        
        # If NaN, default to 0 (neutral momentum)
        df['trend_3'] = (prev_pos - prev_pos_3).fillna(0)

        # 6. Cold Start: Sire Win Rate (Imputation)
        # Calculate Global Sire Stats (This LEAKS future if not done carefully via expanding)
        # But Sire stats are usually considered static properties of the bloodline.
        # Truly efficient way: Calculate Sire Win Rate on the WHOLE dataset (or expanding).
        # Expanding is best for strictness.
        
        grouped_sire = df.groupby('padre')
        sire_wins = grouped_sire['is_win'].shift(1).expanding().sum()
        sire_cnt = grouped_sire['is_win'].shift(1).expanding().count()
        df['sire_win_rate'] = (sire_wins / sire_cnt).fillna(0.10) # Default 10%

        # Impute Main Win Rate for Debutants (races_count == 0)
        # If races_count == 0, use sire_win_rate (plus minimal noise or adjustment? No, simple.)
        mask_debut = (df['races_count'] == 0)
        df.loc[mask_debut, 'win_rate'] = df.loc[mask_debut, 'sire_win_rate']

        # 7. Basic Speed/Rest features (Existing kept for consistency)
        df['prev_date'] = df.groupby('caballo_id')['fecha'].shift(1)
        df['days_rest'] = (df['fecha'] - df['prev_date']).dt.days.fillna(30)
        
        df['seconds'] = df['tiempo'].apply(self._clean_time)
        df['speed_mps'] = np.where(df['seconds'] > 0, df['distancia'] / df['seconds'], 0)
        prev_speed = df.groupby('caballo_id')['speed_mps'].shift(1)
        df['avg_speed_3'] = grouped_horse['speed_mps'].shift(1).rolling(3, min_periods=1).mean().fillna(14) # Check alignment

        # Filter Feature Columns
        X = df[self.feature_cols]
        
        # Final Imputation (Sanity check for inf/nan)
        X = X.replace([np.inf, -np.inf], np.nan)
        
        if is_training:
            self.imputer = SimpleImputer(strategy='median')
            X_imputed = self.imputer.fit_transform(X)
        else:
            if self.imputer:
                X_imputed = self.imputer.transform(X)
            else:
                X_imputed = X.fillna(0) # Fallback

        return pd.DataFrame(X_imputed, columns=self.feature_cols, index=df.index)

    def save(self, path='src/models/feature_eng_v2.pkl'):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self, path)
        print(f"Feature Engineering V2 saved to {path}")

    @staticmethod
    def load(path='src/models/feature_eng_v2.pkl'):
        return joblib.load(path)
