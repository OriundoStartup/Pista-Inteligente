import sys
import os
import pandas as pd

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from src.models.data_manager import obtener_estadisticas_generales

def verify_stats():
    print("--- Verifying Statistics Calculation ---")
    try:
        stats = obtener_estadisticas_generales()
        print("\nStatistics Retrieved:")
        print(f"Total Carreras: {stats.get('total_carreras')}")
        print(f"Aciertos Último Mes: {stats.get('aciertos_ultimo_mes')}%")
        print(f"Dividendos Generados: {stats.get('dividendos_generados')}")
        
        # Assertions
        assert 'aciertos_ultimo_mes' in stats, "Missing 'aciertos_ultimo_mes'"
        assert 'dividendos_generados' in stats, "Missing 'dividendos_generados'"
        
        # Check if values are reasonable (warn if 0, but could be 0 if no data)
        if stats['aciertos_ultimo_mes'] == 0:
            print("WARNING: Accuracy is 0%. Check if there is data for the last 30 days.")
        if stats['dividendos_generados'] == 0:
             print("WARNING: Dividends are 0. Check if there are winning predictions with dividends.")
        
        print("\n--- Verifying Precision View Data Structure ---")
        from src.models.data_manager import calcular_precision_modelo
        precision_data = calcular_precision_modelo()
        
        required_keys = [
            'top1_accuracy', 'top1_correct', 'top1_total',
            'top3_accuracy', 'top3_correct', 'top3_total',
            'top4_accuracy', 'top4_correct', 'top4_total',
            'total_carreras', 'rango_fechas', 'total_dividendos' # Added this one
        ]
        
        missing = [k for k in required_keys if k not in precision_data]
        if missing:
            print(f"ERROR: Missing keys for precision view: {missing}")
            return False
        else:
            print("All required keys for precision logic are present.")

        print("\n--- Verification Successful ---")
        return True
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    verify_stats()
