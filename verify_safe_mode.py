
import sys
# Fix for windows unicode
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from src.models.data_manager import obtener_patrones_la_tercera, obtener_estadisticas_generales

def check():
    print("--- Checking Patterns Safety ---")
    try:
        patrones, timestamp = obtener_patrones_la_tercera()
        print(f"✅ Success! Timestamp: {timestamp}")
        print(f"Count: {len(patrones)}")
    except Exception as e:
        print(f"❌ Failed: {e}")
        
    print("\n--- Checking Statistics ---")
    try:
        stats = obtener_estadisticas_generales()
        print(f"✅ Stats: {stats['total_carreras']} carreras")
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    check()
