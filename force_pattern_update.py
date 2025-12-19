
import sys
import io
# Force UTF-8 for stdout/stderr to avoid emoji crash on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from src.models.data_manager import obtener_patrones_la_tercera
from sync_system import precalculate_patterns

def force_update():
    print("Forcing pattern update...")
    try:
        success = precalculate_patterns(update_mode=True)
        if success:
            print("Successfully updated patterns.")
            # Verify the content
            import json
            with open("data/cache_patrones.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    print(f"Timestamp: {data.get('last_updated')}")
                    print(f"Patterns count: {len(data.get('patterns', []))}")
                else:
                    print("Error: Cache is still a list!")
        else:
            print("Failed to update patterns.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    force_update()
