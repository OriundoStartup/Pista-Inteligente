
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.models.data_manager import obtener_analisis_jornada

def verify():
    print("🔍 Update Check: Testing obtener_analisis_jornada predictions limit...")
    try:
        # Load data
        resultados = obtener_analisis_jornada()
        
        if not resultados:
            print("⚠️ No predictions found for today/future.")
            return

        any_race = resultados[0]
        preds = any_race.get('predicciones', [])
        count = len(preds)
        
        print(f"🏁 Carrera: {any_race['hipodromo']} - {any_race['carrera']}")
        print(f"🔢 Cantidad de predicciones retornadas: {count}")
        
        if count <= 4:
            print("✅ SUCCESS: La lista está limitada a 4 o menos.")
            for i, p in enumerate(preds):
                print(f"   {i+1}. {p['caballo']} ({p['puntaje_ia']}%)")
        else:
            print(f"❌ FAILURE: La lista tiene {count} elementos (Esperado <= 4).")

    except Exception as e:
        print(f"❌ Error running verification: {e}")

if __name__ == "__main__":
    verify()
