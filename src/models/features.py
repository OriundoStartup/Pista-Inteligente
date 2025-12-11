import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer
import joblib
import os

class FeatureEngineering:
    def __init__(self):
        self.encoders = {}
        self.imputer = None
        self.feature_cols = [
            'days_rest', 'avg_pos_3', 'win_rate', 'races_count',
            'jockey_eff', 'distancia', 'avg_speed_3', 'pista_encoded', 'mandil', 'peso'
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

    def fit(self, df):
        """Fit encoders and imputer on training data."""
        df_proc = df.copy()
        
        # Pista Encoder
        le_pista = LabelEncoder()
        # Ensure string and handle nulls
        df_proc['pista'] = df_proc['pista'].fillna('ARENA').astype(str)
        le_pista.fit(df_proc['pista'])
        self.encoders['pista'] = le_pista
        
        # Pre-process designed features to fit Imputer
        # Note: We need to run the transformation to get data for imputer fit
        # usage: fit() is usually called inside pipeline, but we are doing manual steps
        # For simplicity, we will fit imputer in transform or a separate method?
        # Let's just create the imputer here but we need data.
        # So we'll run transform logic inside fit as well roughly or just initiate.
        
        self.imputer = SimpleImputer(strategy='mean')
        return self

    def transform(self, df, is_training=True):
        """Transform raw dataframe into feature matrix."""
        df = df.copy()
        df['fecha'] = pd.to_datetime(df['fecha'])
        df = df.sort_values('fecha')

        # 1. Basic columns cleaning
        df['distancia'] = pd.to_numeric(df['distancia'], errors='coerce').fillna(1000)
        df['mandil'] = pd.to_numeric(df['mandil'], errors='coerce').fillna(0)
        df['peso'] = pd.to_numeric(df['peso_fs'], errors='coerce').fillna(470) # Default weight

        # 2. Historical / Rolling Features
        # Calculate these always as we expect raw data input
        
        # Sort by date for correct rolling
        df = df.sort_values('fecha')

        # Target (might be fake 0 for inference)
        df['is_win'] = (df['posicion'] == 1).astype(int)

        # Recency
        df['prev_date'] = df.groupby('caballo_id')['fecha'].shift(1)
        df['days_rest'] = (df['fecha'] - df['prev_date']).dt.days.fillna(30)
        
        # Avg Position
        df['prev_pos'] = df.groupby('caballo_id')['posicion'].shift(1)
        df['avg_pos_3'] = df.groupby('caballo_id')['prev_pos'].transform(lambda x: x.rolling(3, min_periods=1).mean()).fillna(8)
        
        # Win Rate
        df['prev_wins'] = df.groupby('caballo_id')['is_win'].transform(lambda x: x.shift().expanding().sum())
        df['races_count'] = df.groupby('caballo_id')['is_win'].transform(lambda x: x.shift().expanding().count())
        df['win_rate'] = (df['prev_wins'] / df['races_count']).fillna(0)
        
        # Jockey stats (Expanding window to avoid leakage)
        df['jockey_wins'] = df.groupby('jinete_id')['is_win'].transform(lambda x: x.shift().expanding().sum())
        df['jockey_races'] = df.groupby('jinete_id')['is_win'].transform(lambda x: x.shift().expanding().count())
        df['jockey_eff'] = (df['jockey_wins'] / df['jockey_races']).fillna(0.1)
        
        # Speed
        df['seconds'] = df['tiempo'].apply(self._clean_time)
        df['speed_mps'] = np.where(df['seconds'] > 0, df['distancia'] / df['seconds'], 0)
        df['prev_speed'] = df.groupby('caballo_id')['speed_mps'].shift(1)
        df['avg_speed_3'] = df.groupby('caballo_id')['prev_speed'].transform(lambda x: x.rolling(3, min_periods=1).mean()).fillna(14)


        # Encoding

        if 'pista' in self.encoders:
            # Handle unknown labels
            # map known classes, fill unknown with 0
            # A safer way using sklearn classes directly:
            # But we need to handle potential new tracks.
            try:
                # df['pista_encoded'] = self.encoders['pista'].transform(df['pista'].astype(str))
                # Robust transform
                known_classes = set(self.encoders['pista'].classes_)
                df['pista_clean'] = df['pista'].astype(str).apply(lambda x: x if x in known_classes else list(known_classes)[0])
                df['pista_encoded'] = self.encoders['pista'].transform(df['pista_clean'])
            except:
                df['pista_encoded'] = 0
        else:
            df['pista_encoded'] = 0
            
        # Select Features
        X = df[self.feature_cols]
        
        # Impute
        X = X.replace([np.inf, -np.inf], np.nan)
        if is_training:
            X_imputed = self.imputer.fit_transform(X)
        else:
            X_imputed = self.imputer.transform(X)
            
        return pd.DataFrame(X_imputed, columns=self.feature_cols, index=df.index)

    def save(self, path='src/models/feature_eng_v2.pkl'):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self, path)
        print(f"Feature Engineering saved to {path}")

    @staticmethod
    def load(path='src/models/feature_eng_v2.pkl'):
        return joblib.load(path)
