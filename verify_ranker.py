from src.models.data_manager import analizar_probabilidad_caballos
import pandas as pd
import numpy as np

def verify_ranker():
    print("--- Verifying Softmax Normalization (LGBMRanker) ---")
    
    # Mock Dataframe for a single race
    mock_race = pd.DataFrame([
        {'caballo': 'Caballo A', 'numero': 1, 'jinete': 'Jinete A', 'peso': 480},
        {'caballo': 'Caballo B', 'numero': 2, 'jinete': 'Jinete B', 'peso': 490},
        {'caballo': 'Caballo C', 'numero': 3, 'jinete': 'Jinete C', 'peso': 470},
    ])
    
    # Mock History (Empty is fine, heateristic loop handles it, but let's give some wins)
    mock_history = pd.DataFrame([
        {'caballo': 'Caballo A', 'fecha': '2024-01-01', 'posicion': 1, 'caballo_id': 'cA', 'jinete': 'Jinete A', 'jinete_id': 'jA',
         'distancia': 1000, 'pista': 'ARENA', 'peso_fs': 480, 'mandil': 5, 'tiempo': 60.0},
        {'caballo': 'Caballo B', 'fecha': '2024-01-01', 'posicion': 5, 'caballo_id': 'cB', 'jinete': 'Jinete B', 'jinete_id': 'jB',
         'distancia': 1000, 'pista': 'ARENA', 'peso_fs': 490, 'mandil': 6, 'tiempo': 61.0},
    ])
    
    # Mock Model with 'predict' method (Ranker-like)
    class MockRanker:
        def predict(self, X):
            # Return arbitrary raw scores
            return np.array([2.5, 1.0, 0.5]) # A > B > C

    # Mock FE
    class MockFE:
        def transform(self, df, is_training=False):
            return pd.DataFrame([[0]*5]*len(df)) # Dummy feature vector
            
    mock_model = MockRanker()
    mock_fe = MockFE()
    
    print("\nRunning `analizar_probabilidad_caballos` with Mock Ranker...")
    results = analizar_probabilidad_caballos(mock_race, mock_history, model=mock_model, fe=mock_fe)
    
    print("\nResults:")
    total_prob = 0
    for r in results:
        print(f"Horse {r['numero']}: {r['caballo']} - Prob: {r['prob_ml']}% (IA: {r['puntaje_ia']})")
        total_prob += float(r['prob_ml'])
        
    print(f"\nTotal Sum of ML Probs: {total_prob:.2f}%")
    
    if 99.0 <= total_prob <= 101.0:
        print("✅ SUCCESS: Softmax sums to approx 100%.")
    else:
        print("❌ FAILURE: Does not sum to 100%.")
        
if __name__ == "__main__":
    verify_ranker()
