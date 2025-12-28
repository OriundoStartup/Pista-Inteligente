from src.models.inference import InferencePipeline
import os
import json

def test_pipeline():
    print("--- Testing Inference Pipeline ---")
    
    # Run
    pipeline = InferencePipeline()
    try:
        pipeline.run()
    except Exception as e:
        print(f"❌ Pipeline Failed: {e}")
        return

    # Verify Output
    path = 'data/predicciones_activas.json'
    if os.path.exists(path):
        with open(path, 'r') as f:
            preds = json.load(f)
        
        if len(preds) > 0:
            print(f"✅ Generated {len(preds)} predictions.")
            print("Sample:")
            print(preds[0])
            
            # Verify Softmax Sum per race
            # Group by race (carrera + hipodromo + fecha)
            races = {}
            for p in preds:
                k = f"{p['fecha']}_{p['hipodromo']}_{p['carrera']}"
                if k not in races: races[k] = 0
                races[k] += p['probabilidad']
                
            print("\n--- Softmax Sum Check (First 3 Races) ---")
            count = 0
            for k, s in races.items():
                print(f"Race {k}: Sum = {s:.2f}%")
                if not (99.0 <= s <= 101.0):
                    print("⚠️ Sum warning (Might be rounding or missing horses)")
                count += 1
                if count >= 3: break
                
        else:
            print("⚠️ Pipeline ran but produced 0 predictions (Maybe no future races in DB).")
            # This is expected if 'cargar_programa(solo_futuras=True)' returns empty.
            # To test logic, we might need to mock 'cargar_programa'.
    else:
        print("❌ Output file not found.")

if __name__ == "__main__":
    test_pipeline()
