
import sys
import io
import traceback
# Fix for windows unicode
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from src.models.data_manager import obtener_analisis_jornada

def check_predictions():
    print("--- Checking Predictions Logic ---")
    try:
        analisis = obtener_analisis_jornada()
        print(f"✅ Success! Encoutered {len(analisis)} races.")
        if analisis:
            print("Sample Race 1:")
            print(analisis[0].keys())
            if 'caballos' in analisis[0]:
                print(analisis[0]['caballos'].head(1))
    except Exception as e:
        print("❌ CRITICAL FAILURE:")
        traceback.print_exc()

if __name__ == "__main__":
    check_predictions()
