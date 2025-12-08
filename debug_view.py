from src.models.data_manager import obtener_analisis_jornada

def run():
    print("Testing obtener_analisis_jornada...")
    try:
        data = obtener_analisis_jornada()
        print(f"Total carreras returned: {len(data)}")
        if len(data) > 0:
            print("First race sample:")
            print(data[0]['hipodromo'], data[0]['fecha'], data[0]['carrera'])
            print(f"Predicciones count: {len(data[0]['predicciones'])}")
            print(data[0]['predicciones'][0] if data[0]['predicciones'] else "No predictions")
        else:
            print("No data returned!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run()
