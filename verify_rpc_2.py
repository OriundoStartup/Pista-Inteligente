
import os
import sys
sys.path.append(os.path.abspath('.'))
from src.utils.supabase_client import SupabaseManager

def main():
    client = SupabaseManager()
    supabase = client.get_client()
    
    print("=== VERIFICANDO FUNCIÓN RPC ===")
    try:
        data = supabase.rpc('get_top_jinetes_2026', {}).execute()
        
        print(f"Status: {data}")
        if data.data:
            print(f"✅ RPC Success! Records: {len(data.data)}")
            print("\n🏆 Top 5 Jinetes (RPC):")
            for i, j in enumerate(data.data[:5], 1):
                print(f"   {i}. {j['jinete']} - {j['ganadas']} wins - {j['eficiencia']}%")
        else:
            print("❌ RPC returned no data or failed.")
            print(data)
            
    except Exception as e:
        print(f"❌ Error calling RPC: {e}")

if __name__ == "__main__":
    main()
